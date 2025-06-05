from enum import IntEnum


class Opcode(IntEnum):
    """Basic definitions for Discord operation codes."""

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

    HEARTBEAT_ACK = 6
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

    UNKNOWN_18 = 18
    """Unknown opcode - prevent errors."""

    UNKNOWN_20 = 20
    """Unknown opcode - prevent errors."""

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
