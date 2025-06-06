from __future__ import annotations

from typing import Callable, Union

import asyncio
import struct
import typing

__all__: typing.Sequence[str] = ("VoiceClientProtocol",)


class VoiceClientProtocol(asyncio.DatagramProtocol):
    """UDP client to interact with Discord's voice gateway."""

    def __init__(self, ssrc: int, callback: Callable[[str, int], None]) -> None:
        """
        Create a new UDP client.

        Warning
        -------
        This object should only be instantiated internally.

        Parameters
        ----------
        ssrc : int
            The provided SSRC from Discord's `READY` packet.
        callback : typing.Callable[[str, int], None]
            The synchronous method to call when the device's external UDP IP and port are discovered.
        """
        self._transport: Union[asyncio.DatagramTransport, None] = None
        self._ssrc: int = ssrc
        self._callback: Callable[[str, int], None] = callback

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        """
        Method called automatically when a UDP connection is made.

        Warning
        -------
        - This method should only be called internally.
        - Calling this method may cause issues.
        """
        self._transport = transport

        packet: bytearray = bytearray(74)
        struct.pack_into(">H", packet, 0, 1)
        struct.pack_into(">H", packet, 2, 70)
        struct.pack_into(">I", packet, 4, self._ssrc)

        self._transport.sendto(packet)

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Datagram Received.

        Warning
        -------
        - This method should only be called internally.
        - Calling this method may cause issues.
        """
        if len(data) != 74 or data[1] != 0x02:
            return

        ip: str = data[8 : data.index(0, 8)].decode("ascii")
        port: int = struct.unpack_from(">H", data, len(data) - 2)[0]

        self._callback(ip, port)
