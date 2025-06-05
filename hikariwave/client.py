import asyncio
import logging
import typing

import hikari

import hikariwave.error as errors
from hikariwave.connection import PendingConnection
from hikariwave.connection import VoiceConnection

__all__: typing.Sequence[str] = ("VoiceClient",)

_logger: logging.Logger = logging.getLogger("hikariwave.client")


class VoiceClient:
    """Voice client to interact with Discord's voice system."""

    def __init__(self, bot: hikari.GatewayBot) -> None:
        """
        Create a new voice client to interact with Discord's voice system.

        Parameters
        ----------
        bot : hikari.GatewayBot
            The Discord bot client to interface with.
        """
        self.bot: hikari.GatewayBot = bot
        self.bot.subscribe(hikari.VoiceServerUpdateEvent, self._server_update)
        self.bot.subscribe(hikari.VoiceStateUpdateEvent, self._state_update)

        self._pending_connections: dict[hikari.Snowflake, PendingConnection] = {}
        self._active_connections: dict[hikari.Snowflake, VoiceConnection] = {}

    async def _try_connection(self, guild_id: hikari.Snowflake) -> None:
        pending_connection: PendingConnection = self._pending_connections.get(
            guild_id,
            None,
        )

        if not pending_connection:
            return

        if (
            not pending_connection.endpoint
            or not pending_connection.session_id
            or not pending_connection.token
        ):
            return

        del self._pending_connections[guild_id]

        _logger.debug(
            "Pending connection has now connected with ENDPOINT: %s, SESSION_ID: %s, TOKEN: %s",
            pending_connection.endpoint,
            pending_connection.session_id,
            pending_connection.token,
        )

        self._active_connections[guild_id] = VoiceConnection(self.bot, guild_id)
        await self._active_connections[guild_id].connect(
            pending_connection.endpoint,
            pending_connection.session_id,
            pending_connection.token,
        )

    async def _server_update(self, event: hikari.VoiceServerUpdateEvent) -> None:
        if event.guild_id in self._active_connections:
            return  # Handle later, changed voice servers

        if event.guild_id not in self._pending_connections:
            return

        pending_connection: PendingConnection = self._pending_connections[
            event.guild_id
        ]
        pending_connection.endpoint = event.raw_endpoint
        pending_connection.token = event.token

        _logger.debug(
            "Voice server updated: Received data - ENDPOINT: %s, TOKEN: %s",
            event.raw_endpoint,
            event.token,
        )

        await self._try_connection(event.guild_id)

    async def _state_update(self, event: hikari.VoiceStateUpdateEvent) -> None:
        if event.state.user_id != self.bot.get_me().id:
            return

        if event.guild_id in self._active_connections:
            return

        if event.guild_id not in self._pending_connections:
            return

        self._pending_connections[event.guild_id].session_id = event.state.session_id

        _logger.debug(
            "Voice state updated: Received data - SESSION_ID: %s",
            event.state.session_id,
        )

        await self._try_connection(event.guild_id)

    async def connect(
        self,
        guild_id: hikari.Snowflake,
        channel_id: hikari.Snowflake,
        *,
        mute: bool = False,
        deaf: bool = True,
    ) -> None:
        """
        Connect to a voice channel.

        Parameters
        ----------
        guild_id : hikari.Snowflake
            The ID of the guild that contains the channel.
        channel_id : hikari.Snowflake
            The ID of the channel you wish to connect to.
        mute : bool
            If the bot should join muted.
        deaf : bool
            If the bot should join deafened.

        Raises
        ------
        ConnectionAlreadyEstablishedError
            If the bot is currently in another voice channel.
        """
        if guild_id in self._active_connections:
            return

        self._pending_connections[guild_id] = PendingConnection()
        await self.bot.update_voice_state(
            guild_id,
            channel_id,
            self_mute=mute,
            self_deaf=deaf,
        )

        _logger.info(
            "Connecting to GUILD: %s, CHANNEL: %s - MUTED: %s, DEAFENED: %s",
            guild_id,
            channel_id,
            mute,
            deaf,
        )

    async def disconnect(self, guild_id: hikari.Snowflake) -> None:
        """
        Disconnect from a voice channel.

        Parameters
        ----------
        guild_id : hikari.Snowflake
            The ID of the guild that contains the channel.

        Raises
        ------
        ConnectionNotEstablishedError
            If the bot is not currently connected to a channel in the guild provided.
        """
        if guild_id not in self._active_connections:
            error: str = "No active connection to this guild was found at disconnect"
            raise errors.ConnectionNotEstablishedError(error)

        await self._active_connections[guild_id].close()
        del self._active_connections[guild_id]

        await self.bot.update_voice_state(guild_id, None)

        _logger.info("Disconnected from GUILD: %s", guild_id)

    async def play_file(self, guild_id: hikari.Snowflake, filepath: str) -> None:
        """
        Play audio from a source file.

        Parameters
        ----------
        guild_id : hikari.Snowflake
            The ID of the guild that a current connection exists in.
        filepath : str
            The filepath to the source file.

        Raises
        ------
        ConnectionNotEstablishedError
            If the guild currently does not have an active connection.
        """
        while guild_id in self._pending_connections:
            await asyncio.sleep(0.01)

        connection: VoiceConnection = self._active_connections.get(guild_id, None)

        if not connection:
            error: str = "Can't stream file to a connection that doesn't exist."
            raise errors.ConnectionNotEstablishedError(error)

        await connection._ready_to_send.wait()
        await connection.play_file(filepath)

    async def play_silence(self, guild_id: hikari.Snowflake) -> None:
        """
        Play silent frames of audio.

        Parameters
        ----------
        guild_id : hikari.Snowflake
            The ID of the guild that a current connection exists in.

        Raises
        ------
        ConnectionNotEstablishedError
            If the guild currently does not have an active connection.
        """
        if guild_id not in self._active_connections:
            error: str = "Can't stream file to a connection that doesn't exist."
            raise errors.ConnectionNotEstablishedError(error)

        await self._active_connections[guild_id].play_silence()
