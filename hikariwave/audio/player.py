from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hikariwave.connection import VoiceConnection

from hikariwave.audio.header import Header
from hikariwave.audio.opus import OpusEncoder
from hikariwave.audio.source.base import AudioSource
from hikariwave.constants import Constants
from typing import Callable

import asyncio

class AudioPlayer:
    def __init__(self, connection: 'VoiceConnection') -> None:
        self._connection: 'VoiceConnection' = connection

        self._sequence: int = 0
        self._timestamp: int = 0

        self._encoder: OpusEncoder = OpusEncoder()
        self._task: asyncio.Task = None
        self._playing: bool = False

        self._encryption_mode: Callable[[bytes, bytes], bytes] = getattr(self._connection._encryption, self._connection._mode)
    
    async def _playback(self, source: AudioSource) -> None:
        async for pcm_frame in source.decode():
            if not self._playing or not self._connection._transport:
                break

            opus_packet: bytes = self._encoder.encode(pcm_frame)
            rtp_header: bytes = Header.create_rtp(self._sequence, self._timestamp, self._connection._ssrc)

            encrypted_packet: bytes = self._encryption_mode(rtp_header, opus_packet)
            self._connection._transport.sendto(encrypted_packet)

            self._sequence = (self._sequence + 1) % 65536
            self._timestamp = (self._timestamp + Constants.FRAME_SIZE) % (2 ** 32)

            await asyncio.sleep(Constants.FRAME_LENGTH / 1000)
        
        self._playing = False

    async def play(self, source: AudioSource) -> None:
        if self._playing:
            await self.stop()

        self._playing = True
        self._task = asyncio.create_task(self._playback(source))
    
    async def stop(self) -> None:
        if not self._task:
            return
        
        self._playing = False
        self._task.cancel()

        try:
            await self._task
        except asyncio.CancelledError:
            ...
        
        self._task = None