from dataclasses import dataclass, field
from hikariwave.audio.encryption import EncryptionMode
from hikariwave.audio.player import AudioPlayer
from hikariwave.audio.source.file import FileAudioSource
from hikariwave.audio.source.silent import SilentAudioSource
from hikariwave.constants import Constants
from hikariwave.flag import SpeakingFlag
from hikariwave.opcode import Opcode
from hikariwave.protocol import VoiceClientProtocol
from typing import Callable

import aiohttp
import asyncio
import hikari
import hikariwave.error as errors
import logging
import time

logger: logging.Logger = logging.getLogger("hikariwave.connection")

@dataclass
class PendingConnection:
    """A pending connection to a Discord voice server."""

    endpoint: str = field(default=None)
    """The endpoint in which this connection should connect to when activated."""

    session_id: str = field(default=None)
    """The ID of the session provided by Discord that should be used to connect to/resume a session."""

    token: str = field(default=None)
    """The token provided by Discord that should be used to identify when connecting."""

class VoiceConnection:
    """
    An active connection to a Discord voice server.
    
    Warning
    -------
    This is an internal object and should not be instantiated.
    """

    def __init__(self, bot: hikari.GatewayBot, guild_id: hikari.Snowflake) -> None:
        """
        Instantiate a new active voice connection.
        
        Warning
        -------
        - This object should only be instantiated internally.
        - Instantiating this object may cause issues.
        
        Parameters
        ----------
        bot : hikari.GatewayBot
            The bot instance to interface with.
        guild_id : hikari.Snowflake
            The ID of the guild that this connection is responsible for.
        """
        
        self._bot: hikari.GatewayBot = bot
        self._guild_id: hikari.Snowflake = guild_id

        self._endpoint: str = None
        self._session_id: str = None
        self._token: str = None

        self._websocket: aiohttp.ClientWebSocketResponse = None
        self._ws_sequence: int = 0
        self._running: bool = False

        self._heartbeat_task: asyncio.Task = None
        self._heartbeat_interval: float = 0.0
        self._heartbeat_last_sent: float = time.time()
        self._heartbeat_latency: float = 0.0

        self._ssrc: int = None
        self._ip: str = None
        self._port: int = None
        self._mode: str = None

        self._timestamp: int = None
        self._sequence: int = None

        self._protocol: asyncio.DatagramProtocol = None
        self._transport: asyncio.DatagramTransport = None

        self._external_address_discovered: asyncio.Event = asyncio.Event()
        self._external_ip: str = None
        self._external_port: int = None

        self._secret_key: bytes = None
        self._ready_to_send: asyncio.Event = asyncio.Event()

        self._encryption: EncryptionMode = None
        self._player: AudioPlayer = None

    async def _heartbeat_loop(self) -> None:
        while self._running:
            await asyncio.sleep(self._heartbeat_interval)

            await self._websocket.send_json({
                "op": Opcode.HEARTBEAT,
                'd': {
                    't': int(time.time() * 1000),
                    "seq_ack": self._ws_sequence
                }
            })
            self._heartbeat_last_sent = time.time()

    async def _set_speaking(self, speaking: bool) -> None:
        if not self._websocket:
            return
        
        await self._websocket.send_json({
            "op": Opcode.SPEAKING,
            'd': {
                "speaking": SpeakingFlag.MICROPHONE if speaking else SpeakingFlag.NONE,
                "delay": 0,
                "ssrc": self._ssrc
            }
        })

        logger.debug(f"Set speaking mode to {str(speaking).upper()}")

    async def _websocket_handler(self) -> None:
        async with aiohttp.ClientSession() as session:
            self._websocket = await session.ws_connect(f"wss://{self._endpoint}/?v={Constants.WEBSOCKET_VERSION}")

            await self._websocket.send_json({
                "op": Opcode.IDENTIFY,
                'd': {
                    "server_id": str(self._guild_id),
                    "user_id": str(self._bot.get_me().id),
                    "session_id": self._session_id,
                    "token": self._token
                }
            })

            try:
                async for message in self._websocket:
                    match message.type:
                        case aiohttp.WSMsgType.TEXT:
                            await self._websocket_message(message)
                        case aiohttp.WSMsgType.CLOSE | aiohttp.WSMsgType.CLOSED | aiohttp.WSMsgType.ERROR:
                            logger.debug(f"Connection flagged to close by websocket")
            except Exception as e:
                logger.error(e)
            finally:
                logger.debug(f"Connection with SESSION_ID: {self._session_id} closed")
    
    async def _websocket_message(self, message: aiohttp.WSMessage) -> None:
        payload: dict[str] = message.json()

        opcode: int = payload.get("op", None)
        data: dict[str] = payload.get('d', {})

        self._ws_sequence = payload.get('s', self._ws_sequence)

        match opcode:
            case Opcode.HELLO:
                logger.debug("Received `HELLO` payload - Starting heartbeat")

                self._heartbeat_interval = data["heartbeat_interval"] / 1000
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            case Opcode.HEARTBEAT_ACK:
                self._heartbeat_latency = time.time() - self._heartbeat_last_sent
            case Opcode.READY:
                logger.debug("Received `READY` payload - Discovering IP")

                self._ssrc = data["ssrc"]
                self._ip = data["ip"]
                self._port = data["port"]

                for mode in data["modes"]:
                    encryption_mode: Callable[[bytes, bytes], bytes] = getattr(EncryptionMode, mode, None)

                    if not encryption_mode:
                        continue

                    self._mode = mode
                    break

                if not self._mode:
                    error: str = "No supported encryption mode was found"
                    raise errors.EncryptionModeNotSupportedError(error)
                
                logger.debug(f"READY: SSRC={self._ssrc}, IP={self._ip}, PORT={self._port}, ENCRYPTION_MODE: {self._mode}")

                loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

                def on_ip_discovered(ip: str, port: int) -> None:
                    self._external_ip = ip
                    self._external_port = port
                    self._external_address_discovered.set()

                    logger.debug(f"External IP discovered - {ip}:{port}")
                
                self._transport, self._protocol = await loop.create_datagram_endpoint(
                    lambda: VoiceClientProtocol(self._ssrc, on_ip_discovered),
                    remote_addr=(self._ip, self._port)
                )

                await self._external_address_discovered.wait()
                await self._websocket.send_json({
                    "op": Opcode.SELECT_PROTOCOL,
                    'd': {
                        "protocol": "udp",
                        "data": {
                            "ip": self._external_ip,
                            "port": self._external_port,
                            "mode": mode
                        }
                    }
                })
            case Opcode.RESUMED:
                logger.debug(f"Session resumed after disconnect")
            case Opcode.SESSION_DESCRIPTION:
                self._secret_key = bytes(data["secret_key"])
                self._encryption = EncryptionMode(self._secret_key)
                self._ready_to_send.set()

                logger.debug(f"Session secret key received - Discord servers and client ready for voice packets")

    async def close(self) -> None:
        """
        Close this connection and all subsequent tasks, websockets, and packet transports.
        
        Warning
        -------
        - This method should only be called internally.
        - Calling this method may cause issues.
        """
        
        self._running = False

        await self.stop()

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                ...
            
            self._heartbeat_task = None
        
        if self._websocket and not self._websocket.closed:
            await self._websocket.close()
            self._websocket = None

        if self._transport:
            self._transport.close()
            self._transport = None

    async def connect(self, endpoint: str, session_id: str, token: str) -> None:
        """
        Connect to an endpoint with a session ID and token.
        
        Warning
        -------
        - This method should only be called internally.
        - Calling this method may cause issues.
        """
        
        self._endpoint = endpoint
        self._session_id = session_id
        self._token = token

        self._running = True

        await self._websocket_handler()
    
    async def play_file(self, filepath: str) -> None:
        """
        Play audio from a given filepath.
        
        Warning
        -------
        This method should only be called internally.

        Parameters
        ----------
        filepath : str
            The filepath of the file to stream.
        """
        await self._ready_to_send.wait()
        await self._set_speaking(True)

        source: FileAudioSource = FileAudioSource(filepath)
        self._player = AudioPlayer(self)

        await self._player.play(source)
        await self._set_speaking(False)
    
    async def play_silence(self) -> None:
        """
        Play silent frames of audio.
        
        Warning
        -------
        This method should only be called internally.
        """
        await self._ready_to_send.wait()
        await self._set_speaking(True)

        logger.debug("Playing silent audio frames to current voice channel")

        source: SilentAudioSource = SilentAudioSource()
        self._player = AudioPlayer(self)

        try:
            while self._player:
                await self._player.play(source)
        except asyncio.CancelledError:
            ...
        finally:
            await self._set_speaking(False)
        
        logger.debug("Finished playing silent audio frames to current voice channel")
    
    async def stop(self) -> None:
        """
        Stop the connection from playing audio.
        
        Warning
        -------
        This method should only be called internally.
        """
        if not self._player:
            return
        
        await self._player.stop()
        await self._set_speaking(False)

        self._player = None