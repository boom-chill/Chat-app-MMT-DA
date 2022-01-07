import store
import os
import FTP_Cryptography
import bson
from bson.binary import Binary
import mongodb
from cryptography.fernet import Fernet

files = mongodb.db.files

FILE_DATA = store.FILE_DATA
INFO_FILE = store.INFO_FILE


def check_file_name(file_name):
    return os.path.exists(file_name)


def send_file(socket, file_name):
    file = open(file_name, "rb")
    size = int(os.stat(file_name).st_size)
    socket.send(str(size).encode())

    LISTEN_MSG = socket.recv(1024)

    data = file.read(1024)
    while data:
        socket.send(data)
        data = file.read(1024)


def recv_file(socket, file_name):
    MSG = socket.recv(1024)
    size = int(MSG.decode())

    socket.send("continue".encode())

    time_loop = int(size / 1024)

    if os.path.exists(file_name):
        os.remove(file_name)
    data = b''
    i = 1
    file = open(file_name, "wb")
    while i <= time_loop:
        data = socket.recv(1024)
        file.write(data)
        i = i + 1
    last = size - time_loop*1024
    data = socket.recv(last)
    file.write(data)
    return


# UPLOAD -------------------------------------------------
def send_file_upload(socket, file_name, cryptography):
    file = open(file_name, "rb")
    size = int(os.stat(file_name).st_size)

    INFO_FILE["size"] = size
    INFO_FILE["cryptography"] = cryptography
    INFO_FILE_MSG = store.send_repr(INFO_FILE)
    socket.send(INFO_FILE_MSG)

    LISTEN_MSG = socket.recv(1024)

    data = file.read(1024)
    while data:
        socket.send(data)
        data = file.read(1024)


def recv_file_upload(socket, file_name):
    MSG = socket.recv(1024)
    MSG = store.recv_repr(MSG)
    size = MSG["size"]
    cryptography = MSG["cryptography"]

    socket.send("start".encode())

    time_loop = int(size / 1024)

    file = b''
    data = b''
    i = 1
    while i <= time_loop:
        data = Binary(socket.recv(1024))
        file = file + data
        i = i + 1
    last = size - time_loop*1024
    data = socket.recv(last)
    file = file + data
    insert_file(file_name, file, size, cryptography)
    return


def insert_file(file_name, file, size, cryptography):
    global FILE_DATA
    result = check_file_name_db(file_name)

    if(result != False):
        myquery = {"filename": file_name}
        files.delete_one(myquery)

    FILE_DATA = {
        "_id": file_name,
        "filename": file_name,
        "file": file,
        "size": size,
        "cryptography": cryptography,
    }

    files.insert_one(FILE_DATA)


# DOWNLOAD -------------------------------------------------
def check_file_name_db(filename):
    check_files = {}
    list_files = files.find({"filename": filename})
    for file in list_files:
        check_files = file
    if (check_files != {}):
        return check_files
    else:
        return False


def send_file_download(socket, file_name, cryptography):
    file = check_file_name_db(file_name)
    if(file != False):
        INFO_FILE["size"] = file["size"]
        INFO_FILE["cryptography"] = file["cryptography"]
        INFO_FILE_MSG = store.send_repr(INFO_FILE)
        socket.send(INFO_FILE_MSG)

        LISTEN_MSG = socket.recv(1024)

        socket.send(file['file'])


def recv_file_download(socket, file_name):
    MSG = socket.recv(1024)
    MSG = store.recv_repr(MSG)
    size = MSG["size"]
    cryptography = MSG["cryptography"]

    socket.send("start".encode())

    time_loop = int(size / 1024)

    if os.path.exists(file_name):
        os.remove(file_name)
    save_file = open(file_name, "wb")

    file = b''
    data = b''
    i = 1

    file = Binary(socket.recv(size))

    if(cryptography == True):
        key = FTP_Cryptography.load_key()
        f = Fernet(key)
        data = f.decrypt(file)
    else:
        data = file

    save_file.write(data)
