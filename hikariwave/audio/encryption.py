from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from hikariwave.constants import Constants
from nacl.bindings import crypto_aead_xchacha20poly1305_ietf_encrypt, crypto_secretbox, crypto_secretbox_NONCEBYTES
from nacl.utils import random as nacl_random
from typing import Generator

class EncryptionMode:
    """
    Container class for all supported packet encryption modes.
    
    Warning
    -------
    This is an internal object and should not be instantiated.
    """

    def __init__(self, secret_key: bytes) -> None:
        """
        Create a localized encryption instance.
        
        Warning
        -------
        This is an internal method and should not be called.

        Parameters
        ----------
        secret_key : bytes
            The connection's secret key that was provided by Discord's `SESSION DESCRIPTION` payload.
        
        Raises
        ------
        ValueError
            `secret_key` is not 32 bytes in length.
        """

        if len(secret_key) != 32:
            error: str = "Secret key must be 32 bytes (256 bits) in length"
            raise ValueError(error)
        
        self._secret_key: bytes = secret_key

        self._nonce_lite_generator: Generator[bytes, None, None] = self._generate_nonce_lite()
        self._nonce_rndm_generator: Generator[bytes, None, None] = self._generate_nonce_random()
        self._nonce_strd_generator: Generator[bytes, None, None] = self._generate_nonce_standard()
        self._nonce_xcha_generator: Generator[bytes, None, None] = self._generate_nonce_xchacha()

    def _generate_nonce_lite(self) -> Generator[bytes, None, None]:
        counter: int = 0

        while True:
            yield b"\x00" * 20 + counter.to_bytes(4, "big")

            counter = (counter + 1) % (Constants.BIT_32)

    def _generate_nonce_random(self) -> Generator[bytes, None, None]:
        while True:
            yield nacl_random(crypto_secretbox_NONCEBYTES)

    def _generate_nonce_standard(self) -> Generator[bytes, None, None]:
        counter: int = 0

        while True:
            yield counter.to_bytes(12, "big")

            counter = (counter + 1) % (2 ** 96)

    def _generate_nonce_xchacha(self) -> Generator[bytes, None, None]:
        counter: int = 0

        while True:
            yield counter.to_bytes(24, "big")

            counter = (counter + 1) % (2 ** 192)

    def aead_aes256_gcm(self, header: bytes, data: bytes) -> bytes:
        """
        Encrypts audio data using AEAD AES-256-GCM with an incrementing 12-byte nonce.

        Warning
        -------
        - This encryption method is deprecated by Discord (November 18th, 2024).
        - [https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes](https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes)

        Parameters
        ----------
        header : bytes
            The RTP header used in this encryption.
        data : bytes
            The data to encrypt.

        Returns
        -------
        bytes
            The encrypted audio data.
        """

        nonce: bytes = next(self._nonce_strd_generator)
        ciphertext: bytes = AESGCM(self._secret_key).encrypt(nonce, data, header)

        return header + ciphertext + nonce

    def aead_aes256_gcm_rtpsize(self, header: bytes, data: bytes) -> bytes:
        """
        Encrypts audio data using AEAD AES-256-GCM with a nonce derived from the first 12 bytes of the RTP header.
        
        Parameters
        ----------
        header : bytes
            The RTP header used in this encryption.
        data : bytes
            The data to encrypt.
        
        Returns
        -------
        bytes
            The encrypted audio data.
        """
        
        nonce: bytes = header[:12]
        ciphertext = AESGCM(self._secret_key).encrypt(nonce, data, header)

        return header + ciphertext

    def aead_xchacha20_poly1305_rtpsize(self, header: bytes, data: bytes) -> bytes:
        """
        Encrypts audio data using AEAD AES-XChaCha20-Poly1305 with a 24-byte, incrementing nonce.
        
        Parameters
        ----------
        header : bytes
            The RTP header used in this encryption.
        data : bytes
            The data to encrypt.
        
        Returns
        -------
        bytes
            The encrypted audio data.
        """
        
        nonce: bytes = next(self._nonce_xcha_generator)
        ciphertext: bytes = crypto_aead_xchacha20poly1305_ietf_encrypt(
            data, header, nonce, self._secret_key
        )

        return header + nonce + ciphertext

    def xsalsa20_poly1305(self, header: bytes, data: bytes) -> bytes:
        """
        Encrypts audio data using XSalsa20-Poly1305 with a nonce derived from the RTP header.

        Warning
        -------
        - This encryption method is deprecated by Discord (November 18th, 2024).
        - [https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes](https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes)

        Parameters
        ----------
        header : bytes
            The RTP header used in this encryption.
        data : bytes
            The data to encrypt.

        Returns
        -------
        bytes
            The encrypted audio data.
        """

        nonce: bytes = header.ljust(24, b"\x00")
        ciphertext: bytes = crypto_secretbox(data, nonce, self._secret_key)

        return header + ciphertext
    
    def xsalsa20_poly1305_lite(self, header: bytes, data: bytes) -> bytes:
        """
        Encrypts audio data using XSalsa20-Poly1305 with a 24 byte nonce composed of 20 null bytes followed by a 4 byte counter.

        Warning
        -------
        - This encryption method is deprecated by Discord (November 18th, 2024).
        - [https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes](https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes)

        Parameters
        ----------
        header : bytes
            The RTP header used in this encryption.
        data : bytes
            The data to encrypt.

        Returns
        -------
        bytes
            The encrypted audio data.
        """

        nonce: bytes = next(self._nonce_lite_generator)
        ciphertext: bytes = crypto_secretbox(data, nonce, self._secret_key)

        return header + ciphertext

    def xsalsa20_poly1305_lite_rtpsize(self, header: bytes, data: bytes) -> bytes:
        """
        Encrypts audio data using XSalsa20-Poly1305-Lite with a 24 byte nonce composed of a 4 byte incrementing prefix and 20 trailing null bytes.

        Warning
        -------
        - This encryption method is deprecated by Discord (November 18th, 2024).
        - [https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes](https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes)

        Parameters
        ----------
        header : bytes
            The RTP header used in this encryption.
        data : bytes
            The data to encrypt.

        Returns
        -------
        bytes
            The encrypted audio data.
        """

        full_nonce: bytes = next(self._nonce_strd_generator)
        lite_nonce: bytes = full_nonce[:4]
        nonce: bytes = lite_nonce + b"\x00" * 20

        ciphertext: bytes = crypto_secretbox(data, nonce, self._secret_key)

        return header + ciphertext + lite_nonce
    
    def xsalsa20_poly1305_suffix(self, header: bytes, data: bytes) -> bytes:
        """
        Encrypts audio data using XSalsa20-Poly1305 using a random 24 byte nonce appended to the end of the encrypted packet.

        Warning
        -------
        - This encryption method is deprecated by Discord (November 18th, 2024).
        - [https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes](https://discord.com/developers/docs/topics/voice-connections#transport-encryption-modes)

        Parameters
        ----------
        header : bytes
            The RTP header used in this encryption.
        data : bytes
            The data to encrypt.

        Returns
        -------
        bytes
            The encrypted audio data.
        """

        nonce: bytes = next(self._nonce_rndm_generator)
        ciphertext: bytes = crypto_secretbox(data, nonce, self._secret_key)

        return header + ciphertext + nonce