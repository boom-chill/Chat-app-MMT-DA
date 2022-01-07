import threading
import FTP_core
import socket
import json
from PyQt5.QtCore import *
import time


class FTPClient():

    def __init__(self, host_name, port):
        # QThread.__init__(self)
        self.file = FTP_core.FTPCore()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        while 1:
            try:
                self.s.connect((host_name, int(port)))
                break
            except:
                print("Couldn't connect to server")

    def _get_file(self, json_data, root, callback, bar):
        self.file.get(json_data, root, self.s, callback, bar)
        self.s.recv(1)
        print("Finish recv")

    def get_file(self,  result, file_name, bar, root="upload"):
        header = FTP_core.Header()
        header.action = FTP_core.GET
        header.file_name = file_name
        header.length = 0
        self.s.send(header.to_json_str().encode())

        data = b""
        while b"\r\n\r\n" not in data:
            data += self.s.recv(1)
        data = data.decode()
        print(data)
        data = json.loads(data)
        threading.Thread(target=self._get_file, args=(
            data, root, lambda x: result.emit(x), lambda a: bar.emit(a),)).start()

    def _send_file(self, file, root, callback=None):
        self.file.send(file, root, self.s, callback)
        self.s.recv(1)
        time.sleep(3)
        callback(0)
        print("send")

    def send_file(self, file, root, bar):
        ts = threading.Thread(target=self._send_file, args=(
            file, root, lambda x: bar.emit(x),))
        ts.start()

    def __del__(self):
        print("finish upload/download")
