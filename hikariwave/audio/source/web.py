from hikariwave.audio.source.base import AudioSource
from typing import AsyncIterator

class WebAudioSource(AudioSource):
    def __init__(self, url: str) -> None:
        self._url: str = url
    
    async def decode(self) -> AsyncIterator[bytes]:
        ...