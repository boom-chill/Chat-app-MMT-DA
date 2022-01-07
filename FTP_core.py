import socket
import json
import os

SEND = "send"
GET = "get"


class Header:

    def __int__(self):
        self.action = str
        self.length = 0
        self.file_name = str

    def to_dict(self):
        return dict(action=self.action, length=self.length, file_name=self.file_name)

    def to_json_str(self):
        return json.dumps(self.to_dict()) + "\r\n\r\n"


class FTPCore:
    def __init__(self):
        self.byte = 0
        self.length = 0
        self.ready = False

    def send(self, file_name, root, client: socket, callback=None):
        header = Header()
        header.action = SEND
        header.file_name = file_name
        header.length = 0
        path = root + "/" + file_name

        if os.path.exists(path):
            header.length = os.stat(path).st_size
            self.length = header.length
            client.send(header.to_json_str().encode())
            f = open(path, "rb")
            self.ready = True
            self.byte = 0
            print(header.to_dict())
            while self.byte < header.length:
                data = f.read(4096)
                client.send(data)
                self.byte += len(data)
                if callback is not None:
                    callback(self.byte * 100 / self.length)
        else:
            client.send(header.to_json_str().encode())

    def get(self, header, root, client: socket, callback=None, bar=None):
        self.byte = 0
        print(header)
        file = open(root + '/' + header["file_name"], "wb")
        self.length = header["length"]
        self.ready = True
        if self.length == 0:
            if callback is not None:
                callback(False)
            return False
        while self.byte < header["length"]:
            data = client.recv(1024)
            if len(data) > header["length"]:
                data = data[0:header["length"]]
            self.byte += len(data)
            file.write(data)
            if bar is not None:
                bar(self.byte*100/self.length)
        if callback is not None and bar is not None:
            bar(0)
            callback(True)

        return True
