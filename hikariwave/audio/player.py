from __future__ import annotations

from hikariwave.audio.opus import OpusEncoder
from hikariwave.header import Header
from hikariwave.internal import constants

import asyncio
import typing

if typing.TYPE_CHECKING:
    from hikariwave.audio.source.base import AudioSource
    from hikariwave.connection import VoiceConnection
    
    from typing import Callable

__all__: typing.Sequence[str] = ("AudioPlayer",)


class AudioPlayer:
    """
    Handler class meant to control and handle the playing of audio for each connection.

    Warning
    -------
    This is an internal object and should not be instantiated.
    """

    def __init__(self, connection: VoiceConnection) -> None:
        """
        Instantiate a new audio player.

        Warning
        -------
        This is an internal method and should not be called.

        Parameters
        ----------
        connection : VoiceConnection
            The connection that this player will interface with.
        """
        self._connection: VoiceConnection = connection

        self._sequence: int = 0
        self._timestamp: int = 0

        self._encoder: OpusEncoder = OpusEncoder()
        self._playing: bool = False

        self._encryption_mode: Callable[[bytes, bytes], bytes] = getattr(
            self._connection._encryption,
            self._connection._mode if self._connection._mode else '',
        )

    async def _send_packet(self, frame: bytes) -> None:
        if not frame or not self._connection._transport:
            return

        if (frame_length := len(frame)) < (frame_total := constants.FRAME_SIZE * 4):
            frame += b"\x00" * (frame_total - frame_length)

        opus_packet: bytes = self._encoder.encode(frame)
        rtp_header: bytes = Header.create_rtp(
            self._sequence,
            self._timestamp,
            self._connection._ssrc if self._connection._ssrc else 0,
        )

        encrypted_packet: bytes = self._encryption_mode(rtp_header, opus_packet)
        self._connection._transport.sendto(encrypted_packet)

        self._sequence = (self._sequence + 1) % constants.BIT_16
        self._timestamp = (self._timestamp + constants.FRAME_SIZE) % (constants.BIT_32)

        await asyncio.sleep(constants.FRAME_LENGTH / 1000)

    async def _playback(self, source: AudioSource) -> None:
        try:
            async for pcm_frame in source.decode(): # type: ignore
                if not self._playing or not self._connection._transport:
                    break

                await self._send_packet(pcm_frame) # type: ignore
        except (StopIteration, StopAsyncIteration):
            return

    async def play(self, source: AudioSource) -> None:
        """
        Play the selected audio source and stream it to the connection.

        Warning
        -------
        This is an internal method and should not be called.

        Parameters
        ----------
        source : AudioSource
            The audio source to stream from.
        """
        if self._playing:
            await self.stop()

        self._playing = True

        await self._playback(source)

    async def stop(self) -> None:
        """
        Stop the player from streaming audio to the connection.

        Warning
        -------
        This is an internal method and should not be called.
        """
        self._playing = False
