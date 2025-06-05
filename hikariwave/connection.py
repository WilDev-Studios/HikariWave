import asyncio
import logging
import time
import typing
from dataclasses import dataclass

import aiohttp
import hikari

from hikariwave import voice
from hikariwave.opcodes import Opcode
from hikariwave.protocol import VoiceClientProtocol

_logger: typing.Final[logging.Logger] = logging.getLogger("hikariwave.connection")


@dataclass
class PendingConnection:
    """A pending connection to a Discord voice server."""

    endpoint: str = None
    """The endpoint in which this connection should connect to when activated."""

    session_id: str = None
    """The ID of the session provided by Discord that should be used to connect to/resume a session."""

    token: str = None
    """The token provided by Discord that should be used to identify when connecting."""


class VoiceConnection:
    """An active connection to a Discord voice server."""

    WEBSOCKET_VERSION: int = 8
    """The version of the endpoint to connect to."""

    def __init__(self, bot: hikari.GatewayBot, guild_id: hikari.Snowflake) -> None:
        """Instantiate a new active voice connection.

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
        self._sequence: int = 0
        self._running: bool = False

        self._heartbeat_task: asyncio.Task = None
        self._heartbeat_interval: float = 0.0
        self._heartbeat_last_sent: float = time.time()
        self._heartbeat_latency: float = 0.0

        self._ssrc: int = None
        self._ip: str = None
        self._port: int = None
        self._mode: str = None

        self._protocol: asyncio.DatagramProtocol = None
        self._transport: asyncio.DatagramTransport = None

        self._external_address_discovered: asyncio.Event = asyncio.Event()
        self._external_ip: str = None
        self._external_port: int = None

        self._secret_key: bytes = None
        self._ready_to_send: asyncio.Event = asyncio.Event()

    async def _encrypt_aead_xchacha20_poly1305_rtpsize(self, data: bytes) -> bytes: ...

    async def _heartbeat_loop(self) -> None:
        while self._running:
            heartbeat = voice.Heartbeat(
                timestamp=int(time.time() * 1000),
                sequence_acknowledgement=self._sequence,
            )

            await self._websocket.send_json(voice.encode(heartbeat))

            self._heartbeat_last_sent = time.time()

            await asyncio.sleep(self._heartbeat_interval)

    async def _websocket_handler(self) -> None:
        async with aiohttp.ClientSession() as session:
            self._websocket = await session.ws_connect(
                f"wss://{self._endpoint}/?v={VoiceConnection.WEBSOCKET_VERSION}",
            )

            identify = voice.Identify(
                self._guild_id,
                self._bot.get_me().id,
                self._session_id,
                self._token,
            )

            await self._websocket.send_bytes(voice.encode(identify))

            try:
                async for message in self._websocket:
                    match message.type:
                        case aiohttp.WSMsgType.TEXT:
                            await self._websocket_message(message)
                        case (
                            aiohttp.WSMsgType.CLOSE
                            | aiohttp.WSMsgType.CLOSED
                            | aiohttp.WSMsgType.ERROR
                        ):
                            break
            finally:
                _logger.debug(
                    "Connection with SESSION_ID: %s closed",
                    self._session_id,
                )

    async def _websocket_message(self, message: aiohttp.WSMessage) -> None:
        payload = voice.decode(message.data)

        data = payload.d

        if isinstance(data, voice.Ready):
            _logger.debug("Received `READY` payload - Discovering IP")

            self._ssrc = data.ssrc
            self._ip = data.ip
            self._port = data.port

            for mode in data.modes:
                if not getattr(self, f"_encrypt_{mode}", None):
                    continue

                self._mode = mode

            if not self._mode:
                error: str = "No supported encryption mode was found"
                raise RuntimeError(error)

            loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

            def on_ip_discovered(ip: str, port: int) -> None:
                self._external_ip = ip
                self._external_port = port
                self._external_address_discovered.set()

                _logger.debug("External IP discovered - %s:%s", ip, port)

            self._transport, self._protocol = await loop.create_datagram_endpoint(
                lambda: VoiceClientProtocol(self._ssrc, on_ip_discovered),
                remote_addr=(self._ip, self._port),
            )

            await self._external_address_discovered.wait()
            await self._websocket.send_json(
                {
                    "op": Opcode.SELECT_PROTOCOL,
                    "d": {
                        "protocol": "udp",
                        "data": {
                            "ip": self._external_ip,
                            "port": self._external_port,
                            "mode": self._mode,
                        },
                    },
                },
            )

        if isinstance(data, voice.SessionDescription):
            self._secret_key = bytes(data.secret_key)
            self._ready_to_send.set()

            _logger.debug(
                "Session secret key received.",
            )
            return

        if isinstance(data, voice.Speaking):
            return

        if isinstance(data, voice.HeartbeatAcknowledgement):
            self._heartbeat_latency = time.time() - self._heartbeat_last_sent
            return

        if isinstance(data, voice.Hello):
            self._heartbeat_interval = data.heartbeat_interval / 1000
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            return

        if isinstance(data, voice.Resumed):
            _logger.debug("Session resumed after disconnect")
            return

        if isinstance(data, voice.ClientsConnect):
            return

        if isinstance(data, voice.ClientDisconnect):
            return

        user_only_payloads: typing.Sequence[typing.Any] = (
            voice.Identify,
            voice.SelectProtocol,
            voice.Heartbeat,
            voice.Resume,
        )

        if isinstance(data, user_only_payloads):
            _logger.debug("Received client only OP code: %s", payload.op)
            return

        _logger.debug("Unknown OP code type received: %s", payload.op)

    async def close(self) -> None:
        """
        Close this connection and all subsequent tasks, websockets, and packet transports.

        Warning
        -------
        - This method should only be called internally.
        - Calling this method may cause issues.
        """
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                ...

        if self._websocket and not self._websocket.closed:
            await self._websocket.close()

        if self._transport:
            self._transport.close()

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
