import threading
import socket
import json
import users
from store import *
import file
import FTP_Cryptography
from chatroom import MyWindow
import os
import sys


class load_client:
    def __init__(self, HOST, PORT):
        self.load_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = (HOST, PORT)
        self.load_client.connect(ADDR)
