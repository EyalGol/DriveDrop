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
PORT = 6667
ADDRESS = (IP, PORT)
MAX_USERS = 30
RSA = RsaUtil()
SPECIAL_CHARS = {"interrupt": b"/i0101i/", "recv_file_command": b"/r0101f/", "continue": b"/n0101n/",
                 "authenticate": b"/a0101a/", "list_files": b"/l0101f/", "send_file": b"/r0101r/"}


class Server:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.bind(ADDRESS)
        self.socket.listen(MAX_USERS)
        self.clients = {}
        self.listening_thread = self.client_connection_handling_thread = threading.Thread(
            target=self.handle_new_connection)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        self.client_handling_thread = threading.Thread(target=self.handle_connections)
        self.client_handling_thread.daemon = True
        self.client_handling_thread.start()

    def handle_new_connection(self):
        print("handling new connections")
        try:
            while True:
                conn = self.socket.accept()[0]
                # send RSA key
                conn.send(RSA.public_key.export_key())
                # diffie helmen
                diffie = DiffieUtil()
                diffie.send(conn)
                key = diffie.recv(conn, RSA.private_key)
                self.clients[conn] = key
        except ConnectionError or socket.error:
            del self.clients[conn]

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
        if SPECIAL_CHARS["recv_file_command"] == data:  # recv file transfer
            self.recv_files(conn)
        elif SPECIAL_CHARS["authenticate"] == data:  # authentication request
            self.auth(conn)
        elif SPECIAL_CHARS["list_files"] == data:  # lists available files
            self.list_files(conn)
        elif SPECIAL_CHARS["send_file"] == data:  # send files to the client
            self.send_file(conn)

    def handle_sending(self, conn):
        pass

    def handle_errors(self, conn):
        del self.clients[conn]

    def recv_files(self, conn):
        try:
            key = self.clients[conn]
            conn.send(SPECIAL_CHARS["continue"])
            iv, file_name = loads(conn.recv(2056))
            file_name = AesUtil.decrypt_plaintext(file_name, key, iv)
            conn.send(SPECIAL_CHARS["continue"])
            path = os.path.join(".", "tmp", "(senc){}".format(file_name))
            with open(path, "wb") as f:
                while True:
                    data = conn.recv(2056)
                    if data == SPECIAL_CHARS["interrupt"]:
                        break
                    elif SPECIAL_CHARS["interrupt"] in data:
                        data.strip(SPECIAL_CHARS["interrupt"])
                        f.write(data)
                        break
                    f.write(data)
            conn.send(SPECIAL_CHARS["continue"])
            data = conn.recv(128)
            dest_path = os.path.join(".", "file_db", "{}".format(os.path.split(path)[-1][6:]))
            AesUtil.decrypt_file(path, key, dest_path)
            os.remove(path)
            if data == SPECIAL_CHARS["continue"]:
                conn.send(SPECIAL_CHARS["continue"])
                self.handle_receiving(conn)
        except ConnectionError or TypeError or socket.error:
            del self.clients[conn]

    def auth(self, conn):
        try:
            key = self.clients[conn]
            conn.send(SPECIAL_CHARS["continue"])
            data = AesUtil.decrypt_login(conn.recv(2056), key)
            if data:
                username, password = data
                data = requests.post('http://127.0.0.1:8000/rest-auth/login/',
                                     data={"username": username, "password": password})
                if "key" in data.json():
                    data = requests.get('http://127.0.0.1:8000/users/').json()
                    for user in data:
                        if user["username"] == username:
                            user_groups = []
                            for group in requests.get('http://127.0.0.1:8000/groups/').json():
                                if group["url"] in user["groups"]:
                                    user_groups.append(group["name"])
                            conn.send(dumps(user_groups))
                else:
                    conn.send(dumps(False))
        except ConnectionError or TypeError or socket.error:
            del self.clients[conn]

    def list_files(self, conn):
        key = self.clients[conn]
        file_list = os.listdir(os.path.join(".", "file_db"))
        enc_file_list = []
        iv = b''
        if file_list:
            enc_file, iv = AesUtil.encrypt_plaintext(file_list[0], key)
            enc_file_list.append(enc_file)
            for file in file_list[1:]:
                enc_file, iv = AesUtil.encrypt_plaintext(file, key, iv)
                enc_file_list.append(enc_file)
            conn.send(iv)
            conn.recv(128)
            conn.send(dumps(enc_file_list))
        else:
            conn.send(SPECIAL_CHARS["interrupt"])

    def send_file(self, conn):
        key = self.clients[conn]
        conn.send(SPECIAL_CHARS["continue"])
        iv, file_name = loads(conn.recv(2056))
        file_name = AesUtil.decrypt_plaintext(file_name, key, iv)
        try:
            path = os.path.join(".", "file_db", file_name)
            path = AesUtil.encrypt_file(path, key)
            conn.send(SPECIAL_CHARS["continue"])
            with open(path, 'rb') as f:
                data = f.read(2056)
                while data:
                    conn.send(data)
                    data = f.read(2056)
            conn.send(SPECIAL_CHARS["interrupt"])
            os.remove(path)
        except ConnectionError or TypeError or socket.error:
            del self.clients[conn]
        except FileNotFoundError:
            conn.send(b"The Requested file doesn't exist")


if __name__ == "__main__":
    server = Server()
    sleep(0.5)
    while input("enter stop to close the server: ") != "stop":
        pass
    server.socket.close()
    sys.exit()
