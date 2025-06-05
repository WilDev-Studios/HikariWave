from hikariwave.audio.source.base import AudioSource

class WebAudioSource(AudioSource):
    def __init__(self, url: str) -> None:
        self._url: str = url
    
    async def read(self, n: int) -> bytes:
        ...