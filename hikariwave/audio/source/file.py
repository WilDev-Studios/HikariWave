from collections.abc import AsyncGenerator
from hikariwave.audio.source.base import AudioSource
from hikariwave.constants import Constants
from typing import override

import asyncio

class FileAudioSource(AudioSource):
    """
    File-based audio source implementation.
    
    Warning
    -------
    This is an internal object and should not be instantiated.
    """
    
    def __init__(self, filepath: str) -> None:
        """
        Instantiate a file audio source.
        
        Warning
        -------
        This is an internal method and should not be called.
        
        Parameters
        ----------
        filepath : str
            The path to the file that should be streamed.
        """
        self._filepath: str = filepath
        self._process: asyncio.subprocess.Process = None

    async def _cleanup(self) -> None:
        if not self._process:
            return
        
        try:
            self._process.kill()
            await self._process.wait()
        except:
            pass

        self._process = None

    async def _start(self) -> None:
        self._process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i", self._filepath,
            "-f", Constants.PCM_FORMAT,
            "-ar", str(Constants.SAMPLE_RATE),
            "-ac", str(Constants.CHANNELS),
            "-loglevel", "error",
            "pipe:1",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )

    @override
    async def decode(self) -> AsyncGenerator[bytes, None, None]:
        if self._process is None:
            await self._start()
        
        while True:
            content: bytes = await self._process.stdout.read(Constants.FRAME_SIZE * 4)

            if content:
                yield content
            else:
                break
        
        await self._cleanup()