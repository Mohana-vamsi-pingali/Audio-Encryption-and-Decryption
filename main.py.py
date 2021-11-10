import os
import base64
import time
import struct
import typing
import binascii

from cryptography import utils
from cryptography.hazmat.backends import _get_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.exceptions import InvalidSignature

class InvalidToken(Exception):
    pass

_MAX_CLOCK_SKEW = 60

class Fernet(object):
    def __init__(self, key: bytes, backend=None):
        backend = _get_backend(backend)

        key = base64.urlsafe_b64decode(key)
        if len(key) != 32:
            raise ValueError(
                "Fernet key must be 32 url-safe base64-encoded bytes."
            )

        self._signing_key = key[:16]
        self._encryption_key = key[16:]
        self._backend = backend

    @classmethod
    def generate_key(cls) -> bytes:
        return base64.urlsafe_b64encode(os.urandom(32))

    def encrypt(self, data: bytes) -> bytes:
        return self.encrypt_at_time(data, int(time.time()))

    def encrypt_at_time(self, data: bytes, current_time: int) -> bytes:
        iv = os.urandom(16)
        return self._encrypt_from_parts(data, current_time, iv)

    def _encrypt_from_parts(
        self, data: bytes, current_time: int, iv: bytes
    ) -> bytes:
        utils._check_bytes("data", data)

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encryptor = Cipher(
            algorithms.AES(self._encryption_key), modes.CBC(iv), self._backend
        ).encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        basic_parts = (
            b"\x80" + struct.pack(">Q", current_time) + iv + ciphertext
        )

        h = HMAC(self._signing_key, hashes.SHA256(), backend=self._backend)
        h.update(basic_parts)
        hmac = h.finalize()
        return base64.urlsafe_b64encode(basic_parts + hmac)

    def decrypt(self, token: bytes, ttl: typing.Optional[int] = None) -> bytes:
        timestamp, data = Fernet._get_unverified_token_data(token)
        if ttl is None:
            time_info = None
        else:
            time_info = (ttl, int(time.time()))
        return self._decrypt_data(data, timestamp, time_info)

    def decrypt_at_time(
        self, token: bytes, ttl: int, current_time: int
    ) -> bytes:
        if ttl is None:
            raise ValueError(
                "decrypt_at_time() can only be used with a non-None ttl"
            )
        timestamp, data = Fernet._get_unverified_token_data(token)
        return self._decrypt_data(data, timestamp, (ttl, current_time))

    def extract_timestamp(self, token: bytes) -> int:
        timestamp, data = Fernet._get_unverified_token_data(token)
        # Verify the token was not tampered with.
        self._verify_signature(data)
        return timestamp

    @staticmethod
    def _get_unverified_token_data(token: bytes) -> typing.Tuple[int, bytes]:
        utils._check_bytes("token", token)
        try:
            data = base64.urlsafe_b64decode(token)
        except (TypeError, binascii.Error):
            raise InvalidToken

        if not data or data[0] != 0x80:
            raise InvalidToken

        try:
            (timestamp,) = struct.unpack(">Q", data[1:9])
        except struct.error:
            raise InvalidToken
        return timestamp, data

    def _verify_signature(self, data: bytes) -> None:
        h = HMAC(self._signing_key, hashes.SHA256(), backend=self._backend)
        h.update(data[:-32])
        try:
            h.verify(data[-32:])
        except InvalidSignature:
            raise InvalidToken

    def _decrypt_data(
        self,
        data: bytes,
        timestamp: int,
        time_info: typing.Optional[typing.Tuple[int, int]],
    ) -> bytes:
        if time_info is not None:
            ttl, current_time = time_info
            if timestamp + ttl < current_time:
                raise InvalidToken

            if current_time + _MAX_CLOCK_SKEW < timestamp:
                raise InvalidToken

        self._verify_signature(data)

        iv = data[9:25]
        ciphertext = data[25:-32]
        decryptor = Cipher(
            algorithms.AES(self._encryption_key), modes.CBC(iv), self._backend
        ).decryptor()
        plaintext_padded = decryptor.update(ciphertext)
        try:
            plaintext_padded += decryptor.finalize()
        except ValueError:
            raise InvalidToken
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        unpadded = unpadder.update(plaintext_padded)
        try:
            unpadded += unpadder.finalize()
        except ValueError:
            raise InvalidToken
        return unpadded


#Generate key
def generate_key() -> bytes:
    return base64.urlsafe_b64encode(os.urandom(32))

#encryption 
def encrypt(original_audio_file_path ,encrypted_file_path , key):

    fernet=Fernet(key)

    with open('key.key','wb') as filekey:
        filekey.write(key)

    with open('key.key','rb') as filekey:
        key=filekey.read()

    with open(original_audio_file_path,'rb') as file: #location of voice file to be encrypted
        originalaudio=file.read()

    encrypted=fernet.encrypt(originalaudio)

    with open(encrypted_file_path,'wb') as encrypted_file: #location of newly created voice file after encryption
        encrypted_file.write(encrypted)

    #the encryption audio file is not playable , since all the audio content is encrypted , software apps cannot read the actual data 

#decryption
def decrypt(encrypted_file_path ,decrypted_file_path , key):

    fernet=Fernet(key)

    with open(encrypted_file_path,'rb') as enc_file: #location of newly created voice file to be decrypted
        encrypted=enc_file.read()

    decrypted =fernet.decrypt(encrypted)

    with open(decrypted_file_path,'wb') as dec_file: #location of newly created voice file after decrypted
        dec_file.write(decrypted)


key=generate_key()

#print(key)

encrypt("test.m4a", 'encrypted.wav', key)

decrypt('encrypted.wav', 'decrypted.wav', key)
