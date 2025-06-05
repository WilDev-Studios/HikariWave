from collections.abc import AsyncGenerator
from hikariwave.audio.source.base import AudioSource
from typing import override

class WebAudioSource(AudioSource):
    '''
    Web-based audio source implementation.
    
    Warning
    -------
    This is an internal object and should not be instantiated.
    '''
    
    def __init__(self, url: str) -> None:
        """
        Create a new web audio source.
        
        Warning
        -------
        This is an internal method and should not be called.
        
        Parameters
        ----------
        url : str
            The URL of an audio file.
        """
        self._url: str = url
    
    @override
    async def decode(self) -> AsyncGenerator[bytes]:
        ...