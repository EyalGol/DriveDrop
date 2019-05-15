from Crypto.PublicKey import RSA
from _pickle import dumps, loads
from Crypto.Cipher import AES, PKCS1_OAEP
from base64 import b64encode
from base64 import b64decode
from random import randint
from Crypto.Hash import SHA256
from Crypto import Random
import os

KEY_LENGTH = 1024

BLOCK_SIZE = 16
FILE_CHUNK = 1024 * 16
INTERRUPT = b'\u0101'
PAD = b'0'


class AesUtil(object):
    """
    responsible for the AES encryption and decryption
    """

    # create key from int (Diffie Helmen)
    @staticmethod
    def create_key(num, iv):
        key = s = SHA256.new(str(num).encode("utf8")).digest()
        return AES.new(key, AES.MODE_CBC, iv)

    # Strip your data after decryption (with pad and interrupt)
    @staticmethod
    def strip_padding(data):
        return data.rstrip(PAD).rstrip(INTERRUPT)

    @staticmethod
    # Pad your data before encryption (with pad and interrupt)
    def add_padding(data):
        new_data = b''.join([data, INTERRUPT])
        new_data_len = len(new_data)
        remaining_len = BLOCK_SIZE - new_data_len
        to_pad_len = remaining_len % BLOCK_SIZE
        pad_string = PAD * to_pad_len
        return b''.join([new_data, pad_string])

    @staticmethod
    # Decrypt the given encrypted data with the decryption cypher
    def encrypt_object(object, key):
        packed_object = pack(object)
        enc_object = key.encrypt(packed_object)
        return enc_object

    # Encrypt the given data with the encryption cypher
    @staticmethod
    def decrypt_object(packet_object, key):
        enc_object = unpack(packet_object)
        object = key.decrypt(enc_object)
        return object

    @staticmethod
    def encrypt_file(path, key):
        new_path = os.path.join(".", "tmp", "(enc){}".format(os.path.split(path)[-1]))
        with open(path, 'rb') as rf:
            IV = Random.new().read(16)
            cipher = AesUtil.create_key(key, IV)
            with open(new_path, 'wb') as wf:
                wf.write(IV)
                data = rf.read(FILE_CHUNK)
                if len(data) % BLOCK_SIZE != 0:
                    data = AesUtil.add_padding(data)
                while data:
                    enc_data = cipher.encrypt(data)
                    wf.write(enc_data)
                    data = rf.read(FILE_CHUNK)
                    if len(data) % BLOCK_SIZE != 0:
                        data = AesUtil.add_padding(data)
        return new_path

    @staticmethod
    def decrypt_file(path, key):
        new_path = os.path.join(".", "tmp", "(sdec){}".format(os.path.split(path)[-1][5:]))
        with open(path, 'rb') as rf:
            IV = rf.read(16)
            cipher = AesUtil.create_key(key, IV)
            with open(new_path, 'wb') as wf:
                data = rf.read(FILE_CHUNK)
                while data:
                    print("decrypting...")
                    dec_data = cipher.decrypt(data)
                    wf.write(AesUtil.strip_padding(dec_data))
                    data = rf.read(FILE_CHUNK)
        return new_path


class RsaUtil:
    """
          responsible for the RSA encryption and decryption
          """
    private_key = None

    # creates public and private key
    def __init__(self):
        self.private_key = RSA.generate(KEY_LENGTH)
        self.public_key = self.private_key.publickey()

    @staticmethod
    def pack_encrypt(data, key):  # encrypts data with the public rsa key
        pack_data = pack(data)
        cipher_rsa = PKCS1_OAEP.new(key)
        data = cipher_rsa.encrypt(pack_data)
        return data

    @staticmethod
    def unpack_decrypt(data, key):  # decrypts data with private rsa key
        cipher_rsa = PKCS1_OAEP.new(key)
        decrypt_data = cipher_rsa.decrypt(data)
        return unpack(decrypt_data)

    @staticmethod
    def encrypt(data, key):  # encrypts data with the public rsa key
        cipher_rsa = PKCS1_OAEP.new(key)
        return cipher_rsa.encrypt(data)

    @staticmethod
    def decrypt(data, key):  # decrypts data with private rsa key
        cipher_rsa = PKCS1_OAEP.new(key)
        return cipher_rsa.decrypt(data)


class DiffieUtil:
    def __init__(self):
        self.base = 345
        self.mod = 286
        self.private = randint(100, 999)
        self.pk = self.diffie_algo(self.base, self.private)
        self.key = None

    # diffie helmen algorithm
    def diffie_algo(self, b, p):
        return b ** p % self.mod

    # sending end of diffie helmen with optional rsa key
    def send(self, conn, key=None):
        if key:
            conn.send(RsaUtil.encrypt(pack_int(self.pk), key))
        else:
            conn.send(pack_int(self.pk))

    # receive end of diffie helmen with optional rsa key
    def recv(self, conn, key=None):
        if key:
            data = RsaUtil.decrypt(conn.recv(2056), key)
        else:
            data = conn.recv(2056)
        self.key = self.diffie_algo(int(data), self.private)
        return self.key


def pack(data):
    return b64encode(dumps(data).encode("utf8"))


def unpack(data):
    return loads(b64decode(data).decode("utf8"))


def pack_int(data):
    return str(data).encode("utf8")
