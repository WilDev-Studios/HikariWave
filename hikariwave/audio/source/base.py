from abc import ABC, abstractmethod
from typing import AsyncIterator

class AudioSource(ABC):
    """
    Base audio source implementation.
    
    Warning
    -------
    This is an internal object and should not be instantiated manually.
    """
    
    @abstractmethod
    async def decode(self) -> AsyncIterator[bytes]:
        """
        Yields PCM frames of this source over an asynchronous iterator.

        Warning
        -------
        This is an internal method and should not be called manually.
        """