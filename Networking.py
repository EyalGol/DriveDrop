import socket
from abc import abstractmethod
from time import time


class Connection:
    def __init__(self, cid, addr=None, token=None):
        """
        :param cid: connection id
        :param addr: optional ip address
        :param token: optional access token
        """
        self.id = cid
        self.addr = addr
        if token:
            self.token = (token, time())

    def set_token(self, token):
        # sets token after a connection has been created
        self.token = (token, time())

    def check_token(self, timeout):
        """
        Checks if the token has been expired
        :param timeout: the time after which the token would be considered expired
        :return: True if the token is valid
        """
        if time() - self.token[1] > timeout:
            self.token = None
            return False
        else:
            return True


class Networking:
    def __init__(self):
        self.socket = socket.socket()
        self.end_of_stream = b'/l/e10101e/1/'

    @abstractmethod
    def handshake(self, soc=None):
        assert self.socket or soc, "No socket available"

    def send_bytes(self, data, soc=None):
        """
        Sends a byte object
        :param data: the bytes
        :param soc: optional socket, if not selected will send to the default socket
        :return: if succeeds returns True
        """
        assert self.socket or soc, "No socket available"
        if not soc:
            soc = self.socket
        try:
            soc.send(data)
            soc.send(self.end_of_stream)
            return True
        except Exception as err:
            print(err)
            return False

    def recv_bytes(self, soc=None):
        """
        Receives bytes
        :param soc: optional socket, if not selected will send to the default socket
        :return: if succeeds returns the bytes
        """
        assert self.socket or soc, "No socket available"
        if not soc:
            soc = self.socket
        data = b''
        try:
            received = soc.recv(1024)
            while self.end_of_stream not in received:
                data += received
                received = soc.recv(1024)
            data += received
            data = data.rstrip(self.end_of_stream)
            return data
        except Exception as err:
            print(err)
            return False
