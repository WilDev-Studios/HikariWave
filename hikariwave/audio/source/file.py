from hikariwave.audio.source.base import AudioSource
from hikariwave.constants import Constants

import asyncio

class FileAudioSource(AudioSource):
    def __init__(self, filepath: str) -> None:
        self._filepath: str = filepath
        self._process: asyncio.subprocess.Process = None

    async def _cleanup(self) -> None:
        if not self._process:
            return
        
        self._process.terminate()
        await self._process.wait()

        self._process = None

    async def _start(self) -> None:
        self._process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i", self._filepath,
            "-f", Constants.PCM_FORMAT,
            "-ar", str(Constants.SAMPLE_RATE),
            "-ac", str(Constants.CHANNELS),
            "-loglevel", "quiet",
            "pipe:1",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )

    async def read(self, n: int) -> bytes:
        if self._process is None or self._process.stdout is None:
            await self._start()
        
        data: bytes = await self._process.stdout.read(n)

        if not data:
            await self._cleanup()
        
        return data