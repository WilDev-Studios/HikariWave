import struct

class Header:
    @staticmethod
    def create_rtp(sequence: int, timestamp: int, ssrc: int) -> bytes:
        header: bytes = struct.pack(
            ">BBHII",
            0x80, # Version 2, no padding, no extension, no CSRC
            0x78, # Opus
            sequence,
            timestamp,
            ssrc
        )

        return header