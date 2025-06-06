from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import AsyncGenerator


class AudioSource(ABC):
    """Base audio source implementation.

    Warning
    -------
    This is an internal object and should not be instantiated manually.
    """

    @abstractmethod
    async def decode(self) -> AsyncGenerator[bytes, None]:
        """Yields PCM frames of this source over a generator.

        Warning
        -------
        This is an internal method and should not be called manually.
        """
