from __future__ import annotations

from hikariwave.audio.source.base import AudioSource
from hikariwave.audio.opus import OpusEncoder
from hikariwave.internal import constants
from typing import AsyncGenerator
from typing_extensions import override

class SilentAudioSource(AudioSource):
    """
    Silent audio source implementation.

    Warning
    -------
    This is an internal object and should not be instantiated manually.
    """

    def __init__(self) -> None:
        """
        Create a new silent audio source.

        Warning
        -------
        This is an internal object and should not be instantiated manually.
        """
        self._encoder: OpusEncoder = OpusEncoder()

        self._silent_pcm: bytes = b"\x00" * (
            constants.FRAME_SIZE * constants.CHANNELS * 2
        )

    @override
    async def decode(self) -> AsyncGenerator[bytes, None]: # type: ignore
        while True:
            yield self._silent_pcm
