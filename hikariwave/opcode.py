from enum import IntEnum

class Opcode(IntEnum):
    """Basic definitions for Discord operation codes."""

    IDENTIFY: int = 0
    """Begin a voice websocket connection."""

    SELECT_PROTOCOL: int = 1
    """Select the voice protocol."""

    READY: int = 2
    """Complete the websocket handshake."""

    HEARTBEAT: int = 3
    """Keep the websocket connection alive."""

    SESSION_DESCRIPTION: int = 4
    """Describe the session."""

    SPEAKING: int = 5
    """Indicate which users are speaking."""

    HEARTBEAT_ACK: int = 6
    """Sent to acknowledge a received client heartbeat."""

    RESUME: int = 7
    """Resume a connection."""

    HELLO: int = 8
    """Time to wait between sending heartbeats in milliseconds."""

    RESUMED: int = 9
    """Acknowledge a successful session resume."""

    CLIENTS_CONNECT: int = 11
    """One or more clients have connected to the voice channel."""

    CLIENT_DISCONNECT: int = 13
    """A client has disconnected from the voice channel."""

    DAVE_PREPARE_TRANSITION: int = 21
    """A downgrade from the DAVE protocol is upcoming."""

    DAVE_EXECUTE_TRANSITION: int = 22
    """Execute a previously announced protocol transition."""

    DAVE_TRANSITION_READY: int = 23
    """Acknowledge readiness previously announced transition."""

    DAVE_PREPARE_EPOCH: int = 24
    """A DAVE protocol version or group change is upcoming."""

    DAVE_MLS_EXTERNAL_SENDER: int = 25
    """Credential and public key for MLS external sender."""

    DAVE_MLS_KEY_PACKAGE: int = 26
    """MLS Key Package for pending group member."""

    DAVE_MLS_PROPOSALS: int = 27
    """MLS Proposals to be appended or revoked."""

    DAVE_MLS_COMMIT_WELCOME: int = 28
    """MLS Commit with optional MLS Welcome messages."""

    DAVE_MLS_ANNOUNCE_COMMIT_TRANSITION: int = 29
    """MLS Commit to be processed for upcoming transition."""

    DAVE_MLS_WELCOME: int = 30
    """MLS Welcome to group for upcoming transition."""

    DAVE_MLS_INVALID_COMMIT_WELCOME: int = 31
    """Flag invalid commit or welcome, request re-add."""