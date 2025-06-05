class Constants:
    '''Defined, constant values used across this module.'''

    CHANNELS: int = 2
    '''The required amount of channels that Discord requires when sending voice streams.'''

    FRAME_LENGTH: int = 20
    '''The duration (ms) each frame is.'''

    FRAME_SIZE: int = 960
    '''The required size of each 20ms, 48kHz, stereo, PCM frame.'''

    PCM_FORMAT: str = "s16le"
    '''The format that FFmpeg requires to create PCM audio streams.'''

    SAMPLE_RATE: int = 48000
    '''The sample rate that Discord requires when sending voice streams.'''

    WEBSOCKET_VERSION: int = 8
    '''The voice websocket server version to connect to.'''