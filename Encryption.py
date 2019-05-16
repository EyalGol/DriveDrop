from Crypto.PublicKey import RSA
from _pickle import dumps, loads
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from base64 import b64encode
from base64 import b64decode
from random import randint
from Crypto.Hash import SHA256, SHA384
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
        key = SHA256.new(str(num).encode("utf8")).digest()
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
    def encrypt_file(path, key, new_path=None):
        # generate a new path
        if not new_path:
            new_path = os.path.join(".", "tmp", "(enc){}".format(os.path.split(path)[-1]))
        while os.path.exists(new_path):  # if path already elitist try put copy behind it
            copy_path = list(os.path.split(new_path))
            copy_path[-1] = "(copy)" + copy_path[-1]
            new_path = os.path.join(*copy_path)
        # read old file and write the decrypted file into new_path
        with open(path, 'rb') as rf:
            iv = Random.new().read(16)
            cipher = AesUtil.create_key(key, iv)
            with open(new_path, 'wb') as wf:
                wf.write(iv)
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
    def decrypt_file(path, key, new_path=None):
        # generate a new path
        if not new_path:
            new_path = os.path.join(".", "tmp", "(dec){}".format(os.path.split(path)[-1][5:]))
        while os.path.exists(new_path):  # if path already elitist try put copy behind it
            copy_path = list(os.path.split(new_path))
            copy_path[-1] = "(copy)"+copy_path[-1]
            new_path = os.path.join(*copy_path)
        with open(path, 'rb') as rf:
            iv = rf.read(16)
            cipher = AesUtil.create_key(key, iv)
            with open(new_path, 'wb') as wf:
                data = rf.read(FILE_CHUNK)
                print("decrypting...")
                while data:
                    try:
                        dec_data = cipher.decrypt(data)
                        if not dec_data:
                            break
                    except ValueError:
                        break
                    wf.write(AesUtil.strip_padding(dec_data))
                    data = rf.read(FILE_CHUNK)
        print("done...")
        return new_path

    @staticmethod
    def encrypt_plaintext(text, key, iv=None):
        """
        :return: returns (enc_data, iv)
        """
        if not iv:
            iv = Random.new().read(16)
        cipher = AesUtil.create_key(key, iv)
        return cipher.encrypt(AesUtil.add_padding(text.encode("utf8"))), iv

    @staticmethod
    def decrypt_plaintext(data, key, iv):
        cipher = AesUtil.create_key(key, iv)
        return AesUtil.strip_padding(cipher.decrypt(data)).decode("utf8")

    @staticmethod
    def encrypt_login(username, password, key):
        """
        :return: returns a json object with the ids of:
        (iv=iv, password="encrypted_password", username=" encrypted_username")
        """
        password, iv = AesUtil.encrypt_plaintext(password, key)
        username, iv = AesUtil.encrypt_plaintext(username, key, iv)

        return dumps({'iv': iv, 'username': username, 'password': password})

    @staticmethod
    def decrypt_login(data, key):
        """
        :return: (username, password)
        """
        data = loads(data)
        iv = data["iv"]
        username = AesUtil.decrypt_plaintext(data["username"], key, iv)
        password = AesUtil.decrypt_plaintext(data["password"], key, iv)
        return username, password


class RsaUtil:
    """
    responsible for the RSA encryption and decryption
    """
    private_key = None

    # creates public and private key
    def __init__(self):
        self.private_key = RSA.generate(KEY_LENGTH)
        self.public_key = self.private_key.publickey()
        self.signature = pkcs1_15.new(self.private_key)

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

    @staticmethod
    def sign_data(data, key):
        return pkcs1_15.new(key).sign(SHA384.new(data))

    @staticmethod
    def verify_data(data, key, signature):
        return pkcs1_15.new(key).verify(SHA384.new(data), signature)


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
