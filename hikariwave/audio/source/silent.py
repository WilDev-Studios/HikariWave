from collections.abc import AsyncGenerator
from hikariwave.audio.source.base import AudioSource
from hikariwave.audio.opus import OpusEncoder
from hikariwave.constants import Constants
from typing import override

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

        self._silent_pcm: bytes = b"\x00" * (Constants.FRAME_SIZE * Constants.CHANNELS * 2)
    
    @override
    async def decode(self) -> AsyncGenerator[bytes]:
        while True:
            yield self._silent_pcm