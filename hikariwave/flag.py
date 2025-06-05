from enum import IntEnum

class SpeakingFlag(IntEnum):
    '''Bitfield values representing speaking modes.'''

    NONE: int = 0
    '''No audio will be transmitted.'''

    MICROPHONE: int = 1 << 0
    '''Normal transmission of voice audio.'''

    SOUNDSHARE: int = 1 << 1
    '''Transmission of context audio for video, no speaking indicator.'''

    PRIORITY: int = 1 << 2
    '''Priority speaker, lowering audio of other speakers.'''