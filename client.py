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
import load_client


# gate to connect/ auto
PORT = 1234
# auto get host from your computer
HOST = socket.gethostbyname(socket.gethostname())
# takes exactly one argument (2 given) .Therefor, we have a tuple/ This is an array
ADDR = (HOST, PORT)
socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = str
room_chat = MyWindow
flag = True
host = str
port = int


def start():
    create_connection()
    create_auth_thread()


def create_auth_thread():
    handle_auth_thread = threading.Thread(
        target=__handle_auth, args=())
    handle_auth_thread.start()


def __handle_auth():
    global username
    while True:
        choice = input("LOGIN or REGISTER (l/r):")
        if(choice == "l"):
            login()
            break
        if(choice == "r"):
            register()
            break


# LOGIN -----------------------------------------------------------------
def login():
    global username
    while True:
        # send
        LOGIN_REQ = users.login()
        MSG = send_repr(LOGIN_REQ)
        socket_client.send(MSG)

        MSG = socket_client.recv(1024)
        MSG = recv_repr(MSG)

        if(MSG['response'] == LOGIN_RES['response']):
            DATA = MSG
            username = DATA['username']
            print(f"WELCOME {username}!")
            create_comeinand_thread()
            return

        print("Wrong!")


# REGISTER --------------------------------------------------------------
def register():
    global DATA
    global username
    while True:
        # send
        REGISTER_REQ = users.register()
        MSG = send_repr(REGISTER_REQ)
        socket_client.send(MSG)

        MSG = socket_client.recv(1024)
        MSG = recv_repr(MSG)

        if(MSG['response'] == REGISTER_RES['response']):
            username = MSG['username']
            DATA_REQ = users.info_register(username)
            MSG = send_repr(DATA_REQ)
            socket_client.send(MSG)

            print(f"REGIST COMPLTETE {username}!")
            login()
            return

        print("Your account is existed!")


# COMEINAND --------------------------------------------
def create_comeinand_thread():
    handle_comeinand_thread = threading.Thread(
        target=__handle_comeinand, args=())
    handle_comeinand_thread.start()

    handle_rcv_thread = threading.Thread(
        target=__handle_rcv, args=())
    handle_rcv_thread.start()


def listen():
    MSG = socket_client.recv(1024)
    MSG = recv_repr(MSG)
    return MSG


def __handle_create_room(id_room):
    global room_chat
    room_chat = MyWindow(username, id_room, socket_client)


def __handle_rcv():
    global flag
    global room_chat
    while True:

        LISTEN_MSG = listen()

        if(LISTEN_MSG['response'] == CREATE_ROOM_RES['response']):
            id_room = LISTEN_MSG['id_room']
            handle_create_room = threading.Thread(
                target=__handle_create_room, args=(id_room, ))
            handle_create_room.start()
            return

        if(LISTEN_MSG['response'] == CHECK_PASSWORD_RES['response']):
            if(LISTEN_MSG['content'] == True):
                password = users.change_password()
                CHANGE_PASSWORD_REQ['username'] = username
                CHANGE_PASSWORD_REQ['cryptography'] = LISTEN_MSG['cryptography']

                if(CHANGE_PASSWORD_REQ['cryptography'] == True):
                    c_pwd = FTP_Cryptography.encrypt_str(password)
                    CHANGE_PASSWORD_REQ['password'] = c_pwd
                else:
                    CHANGE_PASSWORD_REQ['password'] = password

                CHANGE_PASSWORD_MSG = send_repr(CHANGE_PASSWORD_REQ)
                socket_client.send(CHANGE_PASSWORD_MSG)
                flag = True
            else:
                print("PASSWORD wrong!")
                flag = True

        if(LISTEN_MSG['response'] == CHAT_ROOM_RES['response']):
            list_online_users = LISTEN_MSG["online_users"]
            print_online_users = "List users is online: "
            for user in list_online_users:
                print_online_users += user + ", "
            print("[SERVER] " + print_online_users)

        if(LISTEN_MSG['response'] == SET_UP_RES['response']):
            if(LISTEN_MSG['content'] == True):
                print(f"Update COMPLETE!")
            else:
                print(f"Update FALSE!")

        if(LISTEN_MSG['response'] == CHECK_USER_RES['response']):
            if(LISTEN_MSG['content'] == False):
                print("Username not exist!")

        if(LISTEN_MSG['response'] == CHECK_USER_FIND_RES['response']):
            if(LISTEN_MSG['content']):
                print("Username exist!")
            else:
                print("Username not exist!")

        if(LISTEN_MSG['response'] == CHECK_USER_ONLINE_RES['response']):
            if(LISTEN_MSG['content']):
                print("User is online!")
            else:
                print("User is not online!")

        if(LISTEN_MSG['response'] == SHOW_DOB_RES['response']):
            print(f"DATE OF BIRTH: {LISTEN_MSG['dob']}")

        if(LISTEN_MSG['response'] == SHOW_NAME_RES['response']):
            print(f"FULLNAME: {LISTEN_MSG['fullname']}")

        if(LISTEN_MSG['response'] == SHOW_NOTE_RES['response']):
            print(f"NOTE: {LISTEN_MSG['note']}")

        if(LISTEN_MSG['response'] == SHOW_ALL_RES['response']):
            print(f"DATE OF BIRTH: {LISTEN_MSG['dob']}")
            print(f"FULLNAME: {LISTEN_MSG['fullname']}")
            print(f"NOTE: {LISTEN_MSG['note']}")
            print(f"ONLINE status: {LISTEN_MSG['online']}")
            print(f"CREATE ACCOUNT DAY: {LISTEN_MSG['date']}")

        if(LISTEN_MSG['response'] == NOTIFICATION_RES['response']):
            print(LISTEN_MSG['content'])

        if(LISTEN_MSG['response'] == DISCONNECT_RES['response']):
            return


def __handle_comeinand():
    global DATA
    global username
    global flag
    while True:
        MSG = ""
        if(flag == True):
            MSG = input()
        LISTEN_MSG = {}
        LISTEN_MSG['response'] = ""
        # out
        if(MSG == "end"):
            DISCONNECT_REQ['username'] = username
            MSG = send_repr(DISCONNECT_REQ)
            socket_client.send(MSG)
            print(DISCONNECT_REQ['request'])
            return

# CHANGE_PASSWORD --------------------------------------------
        if(MSG == "change_password"):
            CHECK_PASSWORD_REQ = users.check_change_password()
            CHECK_PASSWORD_REQ['username'] = username
            CHECK_PASSWORD_MSG = send_repr(CHECK_PASSWORD_REQ)
            socket_client.send(CHECK_PASSWORD_MSG)
            flag = False

# USER --------------------------------------------------------
        # SEND -------------------
        if("check_user" in MSG and MSG != "check_user"):
            text = MSG.split(' ')
            if(len(text) >= 3):
                comeinand = text[1]
                check_username = text[2]

                list_comeinand = ['-find',
                                  '-online',
                                  '-show_date',
                                  '-show_fullname',
                                  '-show_note',
                                  '-show_all'
                                  ]

                if (comeinand not in list_comeinand):
                    print("OPTION ERROR!")
                    for co in list_comeinand:
                        print(co)
                else:
                    check_user_handle(check_username, comeinand)

            if(len(text) == 2):
                comeinand = text[1]
                # check option before send
                list_comeinand = ['-find',
                                  '-online',
                                  '-show_date',
                                  '-show_fullname',
                                  '-show_note',
                                  '-show_all'
                                  ]

                if (comeinand not in list_comeinand):
                    print("OPTION ERROR!")
                    for co in list_comeinand:
                        print(co)

# SETUP --------------------------------------------------------
        # SEND -------------------
        if("setup_info" in MSG and MSG != "setup_info"):
            text = MSG.split(' ')
            if(len(text) >= 3):
                comeinand = text[1]
                change_value = MSG.split(' ', 2)[2]

                list_comeinand = ['-fullname',
                                  '-date',
                                  '-note',
                                  ]

                if (comeinand not in list_comeinand):
                    print("OPTION ERROR!")
                    for co in list_comeinand:
                        print(co)
                else:
                    set_up_handle(username, comeinand, change_value)

            if(len(text) == 2):
                comeinand = text[1]
                # check option before send
                list_comeinand = ['-fullname',
                                  '-date',
                                  '-note',
                                  ]

                if (comeinand not in list_comeinand):
                    print("OPTION ERROR!")
                    for co in list_comeinand:
                        print(co)

# UPLOAD -----------------------------------------------------
        # SEND -----------------------------------------
        if("upload" in MSG and MSG != "upload"):
            text = MSG.split(' ')
            if(len(text) == 2):
                file_name = [text[1]]
                comeinand = "-single_file"

                upload_handle(username, comeinand, file_name)

            if(len(text) >= 3):
                comeinand = text[1]
                # check option
                list_comeinand = ['-change_name',
                                  '-multi_files',
                                  ]

                if (comeinand not in list_comeinand):
                    print("OPTION ERROR!")
                    for co in list_comeinand:
                        print(co)

                if(comeinand == "-change_name"):
                    temp = MSG.split(' ')
                    new_name = temp[2]
                    old_name = temp[3]
                    list_change_name = [new_name, old_name]

                    upload_handle(username, comeinand, list_change_name)

                if(comeinand == "-multi_files"):
                    temp = MSG.split(' ', 2)
                    list_files = temp[2].split(' ')

                    upload_handle(username, comeinand, list_files)


# DOWNLOAD -----------------------------------------------------
        # SEND -----------------------------------------
        if("download" in MSG and MSG != "download"):
            text = MSG.split(' ')
            if(len(text) == 2):
                file_name = [text[1]]
                comeinand = "-single_file"

                download_handle(username, comeinand, file_name)

            if(len(text) >= 3):
                comeinand = text[1]
                # check option
                list_comeinand = ['-change_name',
                                  '-multi_files',
                                  ]

                if (comeinand not in list_comeinand):
                    print("OPTION ERROR!")
                    for co in list_comeinand:
                        print(co)

                if(comeinand == "-change_name"):
                    temp = MSG.split(' ')
                    new_name = temp[2]
                    old_name = temp[3]
                    list_change_name = [new_name, old_name]

                    download_handle(username, comeinand, list_change_name)

                if(comeinand == "-multi_files"):
                    temp = MSG.split(' ', 2)
                    list_files = temp[2].split(' ')

                    download_handle(username, comeinand, list_files)

# CHAT ---------------------------------------------------------------------------
        # SEND CHAT ROOM -----------------------------------------
        if(MSG == "chat room"):
            CHAT_ROOM_REQ["username"] = username
            CHAT_ROOM_MSG = send_repr(CHAT_ROOM_REQ)
            socket_client.send(CHAT_ROOM_MSG)

        # CREATE ROOM -------------------------------------------
        if("create room" in MSG and "with" in MSG and MSG != "create room"):
            text = MSG.split(' ')
            if(len(text) > 4 and text[3] == "with"):
                id_room = text[2]
                temp = MSG.split(' ', 4)
                list_user_room = temp[4].split(' ')

                CREATE_ROOM_REQ["username"] = username
                CREATE_ROOM_REQ["id_room"] = id_room
                CREATE_ROOM_REQ["list_user_room"] = list_user_room
                CREATE_ROOM_MSG = send_repr(CREATE_ROOM_REQ)
                socket_client.send(CREATE_ROOM_MSG)
            else:
                print("create room <id_room> with <user_list>")


# ----------------------------------------------------------


def set_up_handle(username, comeinand, change_value):
    SET_UP_REQ['username'] = username
    SET_UP_REQ['content'] = comeinand
    SET_UP_REQ['change_value'] = change_value
    SET_UP_MSG = send_repr(SET_UP_REQ)
    socket_client.send(SET_UP_MSG)

    # LISTEN -------------------


def check_user_handle(username, comeinand):
    CHECK_USER_REQ['username'] = username
    CHECK_USER_REQ['content'] = comeinand
    CHECK_USER_MSG = send_repr(CHECK_USER_REQ)
    socket_client.send(CHECK_USER_MSG)


# FILE -----------------------------------------------------------
def upload_handle(username, comeinand, list_file):
    global host
    global port
    l_client = load_client.load_client(host, port + 1)
    UPLOAD_REQ['username'] = username
    UPLOAD_REQ['content'] = comeinand

    if(comeinand == "-change_name"):
        new_name = list_file[0]
        UPLOAD_REQ['files'].append(new_name)
        list_file.remove(new_name)

    # check file
    i = 0
    while i < len(list_file):
        if(file.check_file_name(list_file[i]) == False):
            print(f"<{list_file[i]}> DOESN'T EXIST")
            list_file.remove(list_file[i])
        else:
            i += 1

    if(comeinand != "-change_name"):
        UPLOAD_REQ['files'] = list_file

    if(len(list_file) == 0):
        return

    UPLOAD_MSG = send_repr(UPLOAD_REQ)
    l_client.load_client.send(UPLOAD_MSG)
    choice = input("Do you want to encrypt message before sending? (y/n): ")

    if choice == 'y':
        key = FTP_Cryptography.load_key()
        for file_name in list_file:
            FTP_Cryptography.encrypt(file_name, key)
        for file_name in list_file:
            file.send_file_upload(l_client.load_client, file_name, True)
    else:
        for file_name in list_file:
            file.send_file_upload(l_client.load_client, file_name, False)

    if choice == 'y':
        key = FTP_Cryptography.load_key()
        for file_name in list_file:
            FTP_Cryptography.decrypt(file_name, key)

    L_MSG = l_client.load_client.recv(1024)
    L_MSG = recv_repr(L_MSG)

    if(L_MSG['response'] == NOTIFICATION_RES['response']):
        print(L_MSG['content'])


def download_handle(username, comeinand, list_file):
    global host
    global port
    l_client = load_client.load_client(host, port + 1)
    DOWNLOAD_REQ['username'] = username
    DOWNLOAD_REQ['content'] = comeinand

    if(comeinand == "-change_name"):
        new_name = list_file[0]
        DOWNLOAD_REQ['files'].append(new_name)
        list_file.remove(new_name)
    else:
        DOWNLOAD_REQ['files'] = list_file

    if(len(list_file) == 0):
        return

    choice = input("Do you want to encrypt message before sending? (y/n): ")
    while True:
        if(choice == 'y'):
            DOWNLOAD_REQ['cryptography'] = True
            break
        if(choice == 'n'):
            DOWNLOAD_REQ['cryptography'] = False
            break
    DOWNLOAD_MSG = send_repr(DOWNLOAD_REQ)
    l_client.load_client.send(DOWNLOAD_MSG)

    for fi in list_file:
        file.recv_file_download(l_client.load_client, fi)

    L_MSG = l_client.load_client.recv(1024)
    L_MSG = recv_repr(L_MSG)

    if(L_MSG['response'] == NOTIFICATION_RES['response']):
        print(L_MSG['content'])


# CHAT -----------------------------------------------------------
def create_chat_thread():
    handle_messages_send_thread = threading.Thread(
        target=__handle_messages_send, args=())
    handle_messages_send_thread.start()

    handle_messages_rcv_thread = threading.Thread(
        target=__handle_messages_rcv, args=())
    handle_messages_rcv_thread.start()


def __handle_messages_send():
    global username
    while True:
        MSG = input()

        if not ("cie" in MSG):
            CHAT_REQ['username'] = username
            CHAT_REQ['content'] = MSG
            MSG = send_repr(CHAT_REQ)
            socket_client.send(MSG)

    DISCONNECT_REQ['username'] = username
    MSG = send_repr(DISCONNECT_REQ)
    socket_client.send(MSG)
    print(DISCONNECT_REQ['request'])
    return


def __handle_messages_rcv():
    global DATA
    global username
    while True:
        MSG = socket_client.recv(1024)
        MSG = recv_repr(MSG)

        if(MSG['response'] == CHAT_RES['response']):
            print((MSG['content']))

        if(MSG['response'] == NOTIFICATION_RES['response']):
            print(MSG['content'])

        if(MSG['response'] == DISCONNECT_RES['response']):
            return


# CONNECT ---------------------------------------------------------
def create_connection():
    while True:
        choice = input("YOUR HOST or ONOTHER HOST (y/o): ")
        if(choice == "y"):
            your_host()
            break
        if(choice == "o"):
            onother_host()
            break


def your_host():
    global host
    global port
    host = ADDR[0]
    port = ADDR[1]
    socket_client.connect(ADDR)
    # notice on terminal
    print(f"[CONNECT] in HOST: {ADDR[0]}")
    print(f"[CONNECT] in PORT: {ADDR[1]}")


def onother_host():
    global host
    global port
    while True:
        try:
            host = input("Enter HOST: ")
            port = int(input("Enter PORT: "))
            socket_client.connect((host, port))

            break
        except:
            print("CAN NOT connect to the server!")
    # notice on terminal
    print(f"[CONNECT] in HOST: {host}")
    print(f"[CONNECT] in HOST: {port}")


start()
