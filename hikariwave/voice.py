from __future__ import annotations

import enum
import typing

import hikari
import msgspec

__all__: typing.Sequence[str] = (
    "ClientDisconnect",
    "ClientsConnect",
    "EncryptionType",
    "Heartbeat",
    "HeartbeatAcknowledgement",
    "Hello",
    "Identify",
    "Ready",
    "Resume",
    "Resumed",
    "SelectProtocol",
    "SessionDescription",
    "Speaking",
    "SpeakingType",
    "VoiceCode",
    "decode",
    "encode",
)


class VoiceCode(enum.IntEnum):
    """Voice Code.

    Voice websocket OP codes.

    https://discord.com/developers/docs/topics/opcodes-and-status-codes#voice-voice-opcodes
    """

    IDENTIFY = 0
    """Opcode responsible for sending the `Identify` payload."""

    SELECT_PROTOCOL = 1
    """Opcode responsible for sending the `Select Protocol` payload."""

    READY = 2
    """Opcode responsible for receiving the `Ready` payload."""

    HEARTBEAT = 3
    """Opcode responsible for sending the `Heartbeat` payload."""

    SESSION_DESCRIPTION = 4
    """Opcode responsible for receiving the `Session Description` payload."""

    SPEAKING = 5
    """Opcode responsible for sending/receiving the `Speaking` payload."""

    HEARTBEAT_ACKNOWLEDGEMENT = 6
    """Opcode responsible for receiving the `Heartbeat ACK` payload."""

    RESUME = 7
    """Opcode responsible for sending the `Resume` payload."""

    HELLO = 8
    """Opcode responsible for receiving the `Hello` payload."""

    RESUMED = 9
    """Opcode responsible for receiving the `Resumed` payload."""

    CLIENTS_CONNECT = 11
    """Opcode responsible for receiving the `Clients Connect` payload."""

    CLIENT_DISCONNECT = 13
    """Opcode responsible for receiving the `Client Disconnect` payload."""

    DAVE_PREPARE_TRANSITION = 21
    """Opcode responsible for receiving the `DAVE Prepare Transition` payload."""

    DAVE_EXECUTE_TRANSITION = 22
    """Opcode responsible for receiving the `DAVE Execute Transition` payload."""

    DAVE_TRANSITION_READY = 23
    """Opcode responsible for sending the `DAVE Transition Ready` payload."""

    DAVE_PREPARE_EPOCH = 24
    """Opcode responsible for receiving the `DAVE Prepare Epoch` payload."""

    DAVE_MLS_EXTERNAL_SENDER = 25
    """Opcode responsible for receiving the `DAVE MLS External Sender` payload."""

    DAVE_MLS_KEY_PACKAGE = 26
    """Opcode responsible for sending the `DAVE MLS Key Package` payload."""

    DAVE_MLS_PROPOSALS = 27
    """Opcode responsible for receiving the `DAVE MLS Proposals` payload."""

    DAVE_MLS_COMMIT_WELCOME = 28
    """Opcode responsible for sending the `DAVE MLS Commit Welcome` payload."""

    DAVE_MLS_ANNOUNCE_COMMIT_TRANSITION = 29
    """Opcode responsible for receiving the `DAVE MLS Announce Commit Transition` payload."""

    DAVE_MLS_WELCOME = 30
    """Opcode responsible for receiving the `DAVE MLS Welcome` payload."""

    DAVE_MLS_INVALID_COMMIT_WELCOME = 31
    """Opcode responsible for sending the `DAVE MLS Invalid Commit Welcome` payload."""


class EncryptionType(str, enum.Enum):
    """Encryption Type."""


class SpeakingType(enum.IntFlag):
    """Speaking Type."""


VoicePayloadT = typing.TypeVar(
    "VoicePayloadT",
    bound="msgspec.Raw|msgspec.Struct",
)


class VoicePayload(msgspec.Struct, typing.Generic[VoicePayloadT]):
    """FIXME: Documentation."""

    op: VoiceCode
    """The payload's OP code."""

    d: VoicePayloadT
    """The data within the voice payload."""

    seq: int | None = msgspec.field(default=None)
    """FIXME: I actually have no idea what to name this."""


class Identify(msgspec.Struct):
    """Identify.

    The identification information to use, to authenticate with the voice servers.

    **Sent by:** Client
    """

    server_id: hikari.Snowflake
    """The server ID the bot is identifying to."""

    user_id: hikari.Snowflake
    """The bots user ID."""

    session_id: str
    """The channels session ID."""

    token: str
    """The channels token."""


class SelectProtocol(msgspec.Struct):
    """Select Protocol.

    The protocol to use, and the information about the protocol.

    **Sent by:** Client
    """

    protocol: str
    """The protocol to use."""

    data: SelectProtocolData


class SelectProtocolData(msgspec.Struct):
    """Select Protocol Data.

    The data to use with the selected protocol.
    """

    address: str
    """The address to use."""

    port: int
    """The port to use."""

    mode: EncryptionType
    """The encryption type to use."""


class Ready(msgspec.Struct):
    """Ready.

    The information after authentication about the voice server.

    **Sent by:** Server
    """

    ssrc: int

    ip: str

    port: int

    modes: typing.Sequence[EncryptionType]
    """The encryption types supported."""


class Heartbeat(msgspec.Struct):
    """Heartbeat.

    The heartbeat sent to discord to keep the connection alive.

    **Sent by:** Client
    """

    timestamp: int = msgspec.field(name="t")
    """The timestamp."""

    sequence_acknowledgement: int = msgspec.field(name="seq_ack", default=-1)
    """The last seq received."""


class SessionDescription(msgspec.Struct):
    """Session Description.

    The information about the session, after selecting a protocol.

    **Sent by:** Server
    """

    mode: EncryptionType
    """The encryption type to use."""

    secret_key: typing.Sequence[int]
    """The 32 byte array that is used for encrypting voice data."""


class Speaking(msgspec.Struct):
    """Speaking.

    The status of a user speaking.

    **Sent by:** Client and Server
    """

    speaking: SpeakingType
    """The type of speaking to use."""

    delay: int
    """The delay to use."""

    ssrc: int
    """The SSRC to use."""


class HeartbeatAcknowledgement(msgspec.Struct):
    """Heartbeat Acknowledgement.

    The acknowledgement sent when a heartbeat message is received.

    **Sent by:** Server
    """

    timestamp: int = msgspec.field(name="t")
    """The timestamp that was acknowledged."""


class Resume(msgspec.Struct):
    """Resume.

    The resumption of a previous connection.

    **Sent by:** Client
    """

    server_id: hikari.Snowflake
    """The server ID the bot is identifying to."""

    session_id: str
    """The channels sessions ID."""

    token: str
    """The channels token."""

    sequence_acknowledgement: int = msgspec.field(name="seq_ack", default=-1)
    """The last seq received."""


class Hello(msgspec.Struct):
    """Hello.

    The payload received on connection to the voice server websocket.

    **Sent by:** Client
    """

    heartbeat_interval: int
    """The interval between heartbeats."""


class Resumed(msgspec.Struct):
    """Resumed.

    The connection has successfully been resumed.
    """


class ClientsConnect(msgspec.Struct):
    """Clients Connect.

    The clients that have connected.
    """

    user_ids: typing.Sequence[hikari.Snowflake]


class ClientDisconnect(msgspec.Struct):
    """Client Disconnect.

    The client that has disconnected.
    """

    user_id: hikari.Snowflake


VoicePayloadMappingT: typing.Mapping[VoiceCode, type[msgspec.Struct]] = {
    VoiceCode.IDENTIFY: Identify,
    VoiceCode.SELECT_PROTOCOL: SelectProtocol,
    VoiceCode.READY: Ready,
    VoiceCode.HEARTBEAT: Heartbeat,
    VoiceCode.SESSION_DESCRIPTION: SessionDescription,
    VoiceCode.SPEAKING: Speaking,
    VoiceCode.HEARTBEAT_ACKNOWLEDGEMENT: HeartbeatAcknowledgement,
    VoiceCode.RESUME: Resume,
    VoiceCode.HELLO: Hello,
    VoiceCode.RESUMED: Resumed,
    VoiceCode.CLIENTS_CONNECT: ClientsConnect,
    VoiceCode.CLIENT_DISCONNECT: ClientDisconnect,
}


def _enc_hook(obj: typing.Any) -> typing.Any:
    if isinstance(obj, hikari.Snowflake):
        return str(obj)

    return obj


def _dec_hook(type: type, obj: typing.Any) -> typing.Any:
    if type == hikari.Snowflake:
        return hikari.Snowflake(obj)

    return obj


def encode(obj: msgspec.Struct) -> bytes:
    return msgspec.json.encode(
        obj,
        enc_hook=_enc_hook,
    )


def decode(
    payload: str | bytes,
) -> VoicePayload[msgspec.Struct] | VoicePayload[msgspec.Raw]: # FIXME: This should be typed better.
    base = msgspec.json.decode(
        payload,
        strict=True,
        type=VoicePayload[msgspec.Raw],
        dec_hook=_dec_hook,
    )

    payload_inner_type = VoicePayloadMappingT.get(base.op)

    if payload_inner_type:
        return msgspec.json.decode(
            payload,
            strict=True,
            type=VoicePayload[payload_inner_type],
            dec_hook=_dec_hook,
        )

    return base
