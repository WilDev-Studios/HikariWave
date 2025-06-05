import asyncio
import typing
from collections.abc import AsyncGenerator

from hikariwave.audio.source.base import AudioSource
from hikariwave.internal import constants

__all__: typing.Sequence[str] = ("FFmpegDecoder",)


class FFmpegDecoder:
    """FFmpeg process handler and decoder."""

    def __init__(
        self,
        source: AudioSource,
        format_: str = constants.PCM_FORMAT,
    ) -> None:
        """
        Instantiate an FFmpeg decoder.

        Warning
        -------
        This is an internal object and should not be instantiated.
        """
        self._source: AudioSource = source
        self._format: str = format_
        self._process: asyncio.subprocess.Process = None

    async def _cleanup(self) -> None:
        if not self._process:
            return

        if self._process.stdin:
            self._process.stdin.close()

        self._process.terminate()
        await self._process.wait()

        self._process = None

    async def _feed_ffmpeg(self) -> None:
        try:
            while True:
                chunk: bytes = await self._source.read(4096)

                if not chunk:
                    break

                self._process.stdin.write(chunk)
                await self._process.stdin.drain()
        except Exception:
            ...
        finally:
            self._process.stdin.close()

    async def _start(self) -> None:
        self._process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-f",
            self._format,
            "-ar",
            str(constants.SAMPLE_RATE),
            "-ac",
            str(constants.CHANNELS),
            "-i",
            "pipe:0",
            "-f",
            self._format,
            "-ar",
            str(constants.SAMPLE_RATE),
            "-ac",
            str(constants.CHANNELS),
            "-loglevel",
            "quiet",
            "pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )

    async def decode(self) -> AsyncGenerator[bytes]:
        """
        Decode a given source in the decoder.

        Returns
        -------
        collections.abc.AsyncGenerator[bytes]
            An asynchronous generator that yields frames of FFmpeg data.
        """
        await self._start()

        asyncio.create_task(self._feed_ffmpeg())

        while True:
            data: bytes = await self._process.stdout.read(constants.FRAME_SIZE * 4)

            if not data:
                break

            yield data

        await self._cleanup()
