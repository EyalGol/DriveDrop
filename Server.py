from random import randint
from threading import Thread

from Crypto.PublicKey import RSA
from flask import Flask

from Encryption import *
from Networking import *


class Server(Networking, Encryption):
    def __init__(self, addres):
        Networking.__init__(self)
        Encryption.__init__(self, 12345)
        self.running = True
        self.socket.bind(addres)
        self.socket.listen(30)
        self.clients = {}
        self.pri_key = RSA.generate(2048)
        t = Thread(target=self.init_flask)
        t.daemon = True
        t.start()
        t = Thread(target=self.handle_connections)
        t.daemon = True
        t.run()

    def init_flask(self):
        app = Flask(__name__)

        @app.route('/key/')
        def rsa_key():
            return self.pri_key.publickey().export_key()

        app.run(debug=True, use_reloader=False)

    def handshake(self, conn):
        print("im here")
        soc = conn[0]
        addr = conn[1]
        base = 345
        mod = 286
        private = randint(100, 999)
        pk = self.diffie_algo(mod, base, private)

        self.send_bytes(self.sign(pk, self.pri_key), soc)
        self.clients[addr] = self.diffie_algo(mod, self.recv_bytes(soc), private)

    def handle_connections(self):
        while self.running:
            conn = self.socket.accept()
            data = self.recv_bytes(conn[0]).decode()
            print(data)

            if data == "handshake":
                print(1234)
                Thread(target=self.handshake, args=(conn,)).start()


s = Server(("localhost", 6666))
