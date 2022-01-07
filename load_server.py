import threading
import socket
import json
import users
import online
from store import *
import file
from FTP_Cryptography import encrypt_str, decrypt_str


class load_server:
    def __init__(self, PORT):
        HOST = socket.gethostbyname(socket.gethostname())
        self.load_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = (HOST, PORT)
        self.load_server.bind(ADDR)
        self.load_server.listen()
        threading.Thread(target=self.__listen_connection,
                         args=()).start()

    def __listen_connection(self):
        while True:
            try:
                client, addr = self.load_server.accept()
                threading.Thread(target=self.__handle_connection,
                                 args=(client, addr)).start()
            except:
                pass

    def __handle_connection(self, client, addr):
        while True:
            # recieve REQ
            MSG = client.recv(1024)
            MSG = recv_repr(MSG)
            print(MSG)
            # UPLOAD ----------------------------------------------------------------
            if(MSG["request"] == UPLOAD_REQ["request"]):
                for file_name in MSG['files']:
                    file.recv_file_upload(client, file_name)

                print(f"FILE UPLOADED!")

                NOTIFICATION_RES['content'] = "your FILE is uploaded!"
                client.send(send_repr(NOTIFICATION_RES))
                return

            # DOWNLOAD ----------------------------------------------------------------
            if(MSG["request"] == DOWNLOAD_REQ["request"]):
                cryptography = MSG['cryptography']
                for file_name in MSG['files']:
                    file.send_file_download(
                        client, file_name, cryptography)

                print(f"FILE DOWNLOADED!")

                NOTIFICATION_RES['content'] = "your FILE is downloaded!"
                client.send(send_repr(NOTIFICATION_RES))
                return
