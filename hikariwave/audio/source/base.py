from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

class AudioSource(ABC):
    """
    Base audio source implementation.
    
    Warning
    -------
    This is an internal object and should not be instantiated manually.
    """
    
    @abstractmethod
    async def decode(self) -> AsyncGenerator[bytes]:
        """
        Yields PCM frames of this source over an asynchronous generator.

        Warning
        -------
        This is an internal method and should not be called manually.
        """