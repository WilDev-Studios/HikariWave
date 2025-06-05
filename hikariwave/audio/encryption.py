from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from nacl.bindings import crypto_aead_xchacha20poly1305_ietf_encrypt

import nacl.secret as nsecret
import nacl.utils as nutils

class EncryptionMode:
    '''Container class for all supported packet encryption modes.'''

    @staticmethod
    def aead_aes256_gcm_rtpsize(header: bytes, data: bytes, secret_key: bytes) -> bytes:
        '''
        ...
        '''
        
        if len(secret_key) != 32:
            error: str = "Secret key must be 32 bytes (256 bits) long"
            raise ValueError(error)
        
        nonce: bytes = header[:12]
        associated_data: bytes = header

        ciphertext = AESGCM(secret_key).encrypt(nonce, data, associated_data)
        return header + ciphertext

    @staticmethod
    def aead_xchacha20_poly1305_rtpsize(header: bytes, data: bytes, secret_key: bytes) -> bytes:
        '''
        ...
        '''
        
        if len(secret_key) != 32:
            error: str = "Secret key must be 32 bytes (256 bits) long"
            raise ValueError(error)
        
        nonce: bytes = nutils.random(nsecret.SecretBox.NONCE_SIZE + 8)
        ciphertext: bytes = crypto_aead_xchacha20poly1305_ietf_encrypt(
            data, header, nonce, secret_key
        )

        return header + nonce + ciphertext