from enum import IntEnum

class Opcode(IntEnum):
    '''Basic definitions for Discord operation codes.'''

    IDENTIFY: int = 0
    '''Opcode responsible for sending the `Identify` payload.'''

    SELECT_PROTOCOL: int = 1
    '''Opcode responsible for sending the `Select Protocol` payload.'''

    READY: int = 2
    '''Opcode responsible for receiving the `Ready` payload.'''

    HEARTBEAT: int = 3
    '''Opcode responsible for sending the `Heartbeat` payload.'''

    SESSION_DESCRIPTION: int = 4
    '''Opcode responsible for receiving the `Session Description` payload.'''

    SPEAKING: int = 5
    '''Opcode responsible for sending/receiving the `Speaking` payload.'''

    HEARTBEAT_ACK: int = 6
    '''Opcode responsible for receiving the `Heartbeat ACK` payload.'''

    RESUME: int = 7
    '''Opcode responsible for sending the `Resume` payload.'''

    HELLO: int = 8
    '''Opcode responsible for receiving the `Hello` payload.'''

    RESUMED: int = 9
    '''Opcode responsible for receiving the `Resumed` payload.'''

    CLIENTS_CONNECT: int = 11
    '''Opcode responsible for receiving the `Clients Connect` payload.'''

    CLIENT_DISCONNECT: int = 13
    '''Opcode responsible for receiving the `Client Disconnect` payload.'''

    DAVE_PREPARE_TRANSITION: int = 21
    '''Opcode responsible for receiving the `DAVE Prepare Transition` payload.'''

    DAVE_EXECUTE_TRANSITION: int = 22
    '''Opcode responsible for receiving the `DAVE Execute Transition` payload.'''

    DAVE_TRANSITION_READY: int = 23
    '''Opcode responsible for sending the `DAVE Transition Ready` payload.'''

    DAVE_PREPARE_EPOCH: int = 24
    '''Opcode responsible for receiving the `DAVE Prepare Epoch` payload.'''

    DAVE_MLS_EXTERNAL_SENDER: int = 25
    '''Opcode responsible for receiving the `DAVE MLS External Sender` payload.'''

    DAVE_MLS_KEY_PACKAGE: int = 26
    '''Opcode responsible for sending the `DAVE MLS Key Package` payload.'''

    DAVE_MLS_PROPOSALS: int = 27
    '''Opcode responsible for receiving the `DAVE MLS Proposals` payload.'''

    DAVE_MLS_COMMIT_WELCOME: int = 28
    '''Opcode responsible for sending the `DAVE MLS Commit Welcome` payload.'''

    DAVE_MLS_ANNOUNCE_COMMIT_TRANSITION: int = 29
    '''Opcode responsible for receiving the `DAVE MLS Announce Commit Transition` payload.'''

    DAVE_MLS_WELCOME: int = 30
    '''Opcode responsible for receiving the `DAVE MLS Welcome` payload.'''

    DAVE_MLS_INVALID_COMMIT_WELCOME: int = 31
    '''Opcode responsible for sending the `DAVE MLS Invalid Commit Welcome` payload.'''