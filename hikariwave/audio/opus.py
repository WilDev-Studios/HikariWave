from hikariwave.constants import Constants

import os
import sys

script_dir: str = os.path.dirname(os.path.abspath(__file__))
bin_dir: str = os.path.join(script_dir, "bin")

if sys.platform == "win32":
    os.environ["PATH"] = f"{bin_dir};{os.environ['PATH']}"
    os.add_dll_directory(bin_dir)

import opuslib

class OpusEncoder:
    def __init__(self, application: str="audio") -> None:
        self._application: int = self._get_application_mode(application)

        self._encoder: opuslib.Encoder = opuslib.Encoder(
            Constants.SAMPLE_RATE, Constants.CHANNELS, self._application
        )
    
    def _get_application_mode(self, application: str) -> int:
        return {
            "voip": opuslib.APPLICATION_VOIP,
            "audio": opuslib.APPLICATION_AUDIO,
            "lowdelay": opuslib.APPLICATION_RESTRICTED_LOWDELAY
        }.get(application, opuslib.APPLICATION_AUDIO)
    
    def encode(self, pcm_frame: bytes) -> bytes:
        if len(pcm_frame) != Constants.FRAME_SIZE * Constants.CHANNELS * 2:
            error: str = f"PCM frame must be {Constants.FRAME_SIZE * Constants.CHANNELS * 2} bytes"
            raise ValueError(error)
        
        return self._encoder.encode(pcm_frame, Constants.FRAME_SIZE)