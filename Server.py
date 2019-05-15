import socket
import threading
from _pickle import dumps, loads
from base64 import b64decode, b64encode
from Encryption import *
from time import sleep
import sys
from select import select

IP = "localhost"
PORT = 6666
ADDRESS = (IP, PORT)
MAX_USERS = 30
RSA = RsaUtil()
INTERRUPT = b"/S/s0101s/S/"




class Server:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.bind(ADDRESS)
        self.socket.listen(MAX_USERS)
        self.clients = {}
        self.client_connection_handling_thread = threading.Thread(target=self.handle_new_connection).start()
        self.client_handling_thread = threading.Thread(target=self.handle_connections).start()

    def handle_new_connection(self):
        print("handling new connections")
        while True:
            conn = self.socket.accept()[0]
            # send RSA key
            conn.send(RSA.public_key.export_key())
            # diffie helmen
            diffie = DiffieUtil()
            diffie.send(conn)
            key = diffie.recv(conn, RSA.private_key)
            print(key)
            self.clients[conn] = key
            print(conn, "has connected")

    def handle_connections(self):
        while True:
            sockets = self.clients.keys()
            while not sockets:
                sleep(0.1)
                sockets = self.clients.keys()
            rlist, wlist, elist = select(sockets, sockets, sockets)
            for conn in rlist:
                self.handle_receiving(conn)
            for conn in wlist:
                self.handle_sending(conn)

    def handle_receiving(self, conn):
        # receiving a code (what operation to do)
        code = int(conn.recv(8))
        if code == 1:  # file transfer
            self.recv_files(conn)

    def handle_sending(self, conn):
        pass

    def recv_files(self, conn):
        key = self.clients[conn]
        file_name = conn.recv(1024).decode('utf8')
        path = os.path.join(".", "tmp", "(senc){}".format(file_name))
        with open(path, "wb") as f:
            while True:
                data = conn.recv(2056)
                if data == INTERRUPT:
                    break
                elif INTERRUPT in data:
                    data.strip(INTERRUPT)
                    f.write(data)
                    break
                f.write(data)
                print("receiving...")
        print("done...")
        AesUtil.decrypt_file(path, key)
        print("done...")

if __name__ == "__main__":
    server = Server()
    sleep(0.2)
    while input("enter stop to close the server: ") != "stop":
        pass
    server.socket.close()
    sys.exit()
