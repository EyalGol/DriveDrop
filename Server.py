import socket
import threading
from _pickle import dumps, loads
from base64 import b64decode, b64encode
from Encryption import *
from time import sleep
import sys
from select import select
import requests
import json

IP = "localhost"
PORT = 6669
ADDRESS = (IP, PORT)
MAX_USERS = 30
RSA = RsaUtil()
SPECIAL_CHARS = {"interrupt": b"/i0101i/", "recv_file_command": b"/r0101f/", "continue": b"/n0101n/", 
                 "authenticate": b"/a0101a/"}


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
            for conn in elist:
                self.handle_errors(conn)

    def handle_receiving(self, conn):
        # receiving a code (what operation to do)
        data = conn.recv(128)
        if SPECIAL_CHARS["recv_file_command"] in data:  # recv file transfer
            self.recv_files(conn)
        if SPECIAL_CHARS["authenticate"]:  # authentication request
            self.auth(conn)
            
    def handle_sending(self, conn):
        pass
    
    def handle_errors(self, conn):
        pass

    def recv_files(self, conn):
        key = self.clients[conn]
        conn.send(SPECIAL_CHARS["continue"])
        file_name = conn.recv(2056).decode("utf8")
        conn.send(SPECIAL_CHARS["continue"])
        path = os.path.join(".", "tmp", "(senc){}".format(file_name))
        with open(path, "wb") as f:
            print("receiving...")
            while True:
                data = conn.recv(2056)
                if data == SPECIAL_CHARS["interrupt"]:
                    break
                elif SPECIAL_CHARS["interrupt"] in data:
                    data.strip(SPECIAL_CHARS["interrupt"])
                    f.write(data)
                    break
                f.write(data)
        print("done...")
        conn.send(SPECIAL_CHARS["continue"])
        data = conn.recv(128)
        dest_path = os.path.join(".", "file_db", "{}".format(os.path.split(path)[-1][6:]))
        AesUtil.decrypt_file(path, key, dest_path)
        os.remove(path)
        if data == SPECIAL_CHARS["continue"]:
            conn.send(SPECIAL_CHARS["continue"])
            self.handle_receiving(conn)

    def auth(self, conn):
        key = self.clients[conn]
        conn.send(SPECIAL_CHARS["continue"])
        username, password = AesUtil.decrypt_login(conn.recv(2056), key)
        data = requests.post('http://127.0.0.1:8000/rest-auth/login/',
                             data={"username": username, "password": password})
        if "key" in data.json():
            data = requests.get('http://127.0.0.1:8000/users/').json()
            for user in data:
                if user["username"] == username:
                    conn.send(dumps(user["groups"]))
        else:
            conn.send(dumps(False))


if __name__ == "__main__":
    server = Server()
    sleep(0.5)
    while input("enter stop to close the server: ") != "stop":
        pass
    server.socket.close()
    sys.exit()
