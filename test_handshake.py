from unittest import TestCase

from Client import Client
from Server import Server


class TestHandshake(TestCase):
    def test_handshake(self):
        try:
            client = Client(("localhost", 6666))
            server = Server()
        except Exception as err:
            print(err)
            self.fail()
