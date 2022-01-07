import FTP_core
import socket
import threading
import errno
import json


class FTPServer:
    timeout_seconds = 180

    def __init__(self, port, callback: callable):
        self.FTP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(socket.gethostname())
        self.FTP_socket.bind((host, port))
        print("Starting FTP Server")
        print('Running on host: ' + str(host))
        print('Running on port: ' + str(port))
        print('')
        self.FTP_socket.listen(100)
        # self.FTP_socket.settimeout(self.timeout_seconds)
        threading.Thread(target=self.__listen_connection,
                         args=(callback, )).start()

    def __listen_connection(self, callback: callable):
        while True:
            try:
                connection, address = self.FTP_socket.accept()
                threading.Thread(target=self.__handle_connection,
                                 args=(connection, callback,)).start()
            except:
                pass

    @staticmethod
    def __handle_connection(connection, callback: callable):
        try:
            data = b""
            while b"\r\n\r\n" not in data:
                data += connection.recv(1)
            data = data.decode()
            ftp = FTP_core.FTPCore()
            if data != "":
                data = json.loads(data)
            if data['action'] == FTP_core.GET:
                ftp.send(data["file_name"], "upload", connection)
            if data['action'] == FTP_core.SEND:
                ftp.get(data, "upload", connection)

            connection.send(b'')
            connection.close()
            callback()
        except socket.error as err:
            if err.errno == errno.ECONNRESET:
                print("Client disconnected")
