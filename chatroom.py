from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
import sys
from store import *
import threading


class MyWindow:
    def __init__(self, name, id_room, client):
        app = QApplication(sys.argv)
        self.win = QMainWindow()

        self.name = name
        self.id_room = id_room
        self.client = client
        self.mess = []

        self.win.setGeometry(300, 300, 300, 440)
        self.win.setWindowTitle("CHAT ROOM: " + id_room)
        self.initUI()

        rcv = threading.Thread(target=self.receive)
        rcv.start()

        self.win.show()
        print("START WINDOW")
        sys.exit(app.exec_())

    def initUI(self):
        self.label_name = QtWidgets.QLabel(self.win)
        self.label_name.setText(self.name)
        self.label_name.move(150, 0)

        self.mess_entry = QtWidgets.QLineEdit(self.win)
        self.mess_entry.setFixedWidth(200)
        self.mess_entry.move(10, 360)

        self.send_btn = QtWidgets.QPushButton(self.win)
        self.send_btn.setText("Send")
        self.send_btn.setFixedWidth(80)
        self.send_btn.move(215, 360)
        self.send_btn.clicked.connect(lambda: self.sendMess())

        self.view = QtWidgets.QListWidget(self.win)
        self.view.setFixedWidth(280)
        self.view.setFixedHeight(300)
        self.view.move(10, 35)

        self.close_btn = QtWidgets.QPushButton(self.win)
        self.close_btn.move(10, 400)
        self.close_btn.setText("Quit")
        self.close_btn.setFixedWidth(285)
        self.close_btn.clicked.connect(lambda: self.win.close())

    def sendMess(self):  # doi t tí ok
        if(self.mess_entry.text() != ""):
            CHAT_REQ['id_room'] = self.id_room
            CHAT_REQ['username'] = self.name
            CHAT_REQ['content'] = self.mess_entry.text()
            CHAT_MSG = send_repr(CHAT_REQ)
            self.client.send(CHAT_MSG)

            self.mess.append('[Me] ' + self.mess_entry.text())
            self.view.addItems(self.mess)
            self.mess.clear()
            self.mess_entry.setText('')

    def receive(self):
        while True:
            try:
                MSG = self.client.recv(1024)
                MSG = recv_repr(MSG)
                # insert messages to text box
                self.mess.append(MSG['content'])
                self.view.addItems(self.mess)
                self.mess.clear()
            except:
                # an error will be printed on the command line or console if there's an error
                print("An error occured!")
                DISCONNECT_REQ['username'] = self.name
                self.client.send(send_repr(DISCONNECT_REQ))
                return

    def recv(self, MSG):
        self.mess.append(MSG)
        self.view.addItems(self.mess)
        self.mess.clear()
