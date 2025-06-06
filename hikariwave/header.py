from __future__ import annotations

import struct
import typing

__all__: typing.Sequence[str] = ("Header",)


class Header:
    """Container class for generating headers."""

    @staticmethod
    def create_rtp(sequence: int, timestamp: int, ssrc: int) -> bytes:
        """
        Create an RTP header.

        Warning
        -------
        This is an internal method and should not be called.

        Parameters
        ----------
        sequence : int
            The sequence of the connection sending this header.
        timestamp : int
            The timestamp of the Opus frame being sent.
        ssrc : int
            The SSRC of the connection sending this header - Provided by Discord's `READY` payload.

        Returns
        -------
        bytes
            The fully formed and formatted RTP header.
        """
        header: bytes = struct.pack(
            ">BBHII",
            0x80,  # Version 2, no padding, no extension, no CSRC
            0x78,  # Opus
            sequence,
            timestamp,
            ssrc,
        )

        return header
