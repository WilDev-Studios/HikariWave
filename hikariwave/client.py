import logging
from collections.abc import MutableMapping

import hikari

from hikariwave.connection import PendingConnection
from hikariwave.connection import VoiceConnection


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

        self._logger: logging.Logger = logging.getLogger("hikariwave.client")
        self._logger.setLevel(logging.NOTSET)
        self._logger.propagate = True

        self._pending_connections: MutableMapping[
            hikari.Snowflake,
            PendingConnection,
        ] = {}
        self._active_connections: MutableMapping[hikari.Snowflake, VoiceConnection] = {}

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

        self._logger.debug(
            "Connected successfully: ENDPOINT: %s, SESSION_ID: %s, TOKEN: %s",
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

        self._logger.debug(
            f"Voice server updated: Received data - ENDPOINT: {event.raw_endpoint}, TOKEN: {event.token}",
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

        self._logger.debug(
            f"Voice state updated: Received data - SESSION_ID: {event.state.session_id}",
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
        RuntimeError
            If the bot is currently in another voice channel.
        """
        if guild_id in self._active_connections:
            error: str = (
                "Disconnect from the current channel before connecting to another"
            )
            raise RuntimeError(error)

        self._pending_connections[guild_id] = PendingConnection()
        await self.bot.update_voice_state(
            guild_id,
            channel_id,
            self_mute=mute,
            self_deaf=deaf,
        )

        self._logger.info(
            f"Connecting to GUILD: {guild_id}, CHANNEL: {channel_id} - MUTED: {mute}, DEAFENED: {deaf}",
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
        RuntimeError
            If the bot is not currently connected to a channel in the guild provided.
        """
        if guild_id not in self._active_connections:
            error: str = "No active connection to this guild was found at disconnect"
            raise RuntimeError(error)

        await self.bot.update_voice_state(guild_id, None)

        await self._active_connections[guild_id].close()
        del self._active_connections[guild_id]

        self._logger.info(f"Disconnected from GUILD: {guild_id}")
