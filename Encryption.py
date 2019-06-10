import _pickle as pickle
import json

from Crypto import Random, Signature
from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256


class Encryption:
    def __init__(self, aeskey):
        self.key = SHA3_256.new(str(aeskey).encode()).digest()

    def get_cypher(self, iv):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return cipher
        except Exception as err:
            print(err)
            return False

    @staticmethod
    def strip_padding(data):
        # Strip your data after decryption (with pad and interrupt)
        interrupt = b'\u0101'
        pad = b'0'
        return data.rstrip(pad).rstrip(interrupt)

    @staticmethod
    def add_padding(data):
        # Pad your data before encryption (with pad and interrupt)
        interrupt = b'\u0101'
        pad = b'0'
        block_size = 16
        new_data = b''.join([data, interrupt])
        new_data_len = len(new_data)
        remaining_len = block_size - new_data_len
        to_pad_len = remaining_len % block_size
        pad_string = pad * to_pad_len
        return b''.join([new_data, pad_string])

    def encrypt(self, data, iv=None):
        try:
            json.dumps(data)
        except Exception as err:
            print(err)
            return False
        if not iv:
            iv = Random.new().read(16)
        cipher = self.get_cypher(iv)
        try:
            enc_data = cipher.encrypt(self.add_padding(data.encode("utf8")))
            return pickle.dumps({"iv": iv, "data": enc_data})
        except Exception as err:
            print(err)
            return False

    def decrypt(self, data):
        cipher = self.get_cypher(data["iv"])
        try:
            data = pickle.loads(data["data"])
            dec_data = cipher.decrypt(data["data"])
            return json.loads(dec_data)
        except Exception as err:
            print(err)
            return False

    @staticmethod
    def sign(data, pri_key):
        cipher = Signature().pkcs1_15.new(pri_key)
        msg_hash = SHA3_256.new(data)
        signature = cipher.sign(msg_hash)
        return pickle.dumps(json.dumps({"signature": signature, "data": data}))

    @staticmethod
    def check_signature(data, pub_key):
        data = json.loads(pickle.loads(data))
        try:
            cipher = Signature.pkcs1_15.new(pub_key)
            msg_hash = SHA3_256.new(data["data"])
            cipher.verify(msg_hash, data["signature"])
            return data["data"]
        except ValueError as err:
            print(err)
            return False

    @staticmethod
    def diffie_algo(mod, b, p):
        return b ** p % mod
