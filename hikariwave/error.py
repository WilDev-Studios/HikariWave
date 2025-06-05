class ConnectionAlreadyEstablishedError(RuntimeError):
    """Thrown when an attempt to create a new connection occurs when a connection already exists."""

class ConnectionNotEstablishedError(RuntimeError):
    """Thrown when an attempt to manipulate a connection occurs when the connection doesn't exist."""

class EncryptionModeNotSupportedError(RuntimeError):
    """Thrown when an attempt to use an unsupported encryption mode occurs."""