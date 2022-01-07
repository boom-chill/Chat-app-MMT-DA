import threading
import socket
import json
import users
import online
from store import *
import file
from FTP_Cryptography import encrypt_str, decrypt_str
import load_server

# gate to connect/ auto
PORT = 1234
# auto get host from your computer
HOST = socket.gethostbyname(socket.gethostname())
# takes exactly one argument (2 given) .Therefor, we have a tuple/ This is an array
ADDR = (HOST, PORT)
# client online
online_users = []
clients = set()
rooms = []

socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.bind(ADDR)


def start():
    l_server = load_server.load_server(PORT + 1)
    # notice on terminal
    print(f"[SERVER RUNNING] at HOST: {ADDR[0]}")
    print(f"[SERVER RUNNING] at PORT: {ADDR[1]}")
    socket_server.listen()

    # starting thread to accept connect from client
    while True:
        client, addr = socket_server.accept()
        # add clients to manage
        clients.add(client)

        handle_client_thread = threading.Thread(
            target=handle_client, args=(client, addr))
        handle_client_thread.start()
        # notice on terminal
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 4}")


def check_online_user(username):
    global online_users
    for user in online_users:
        if(user["username"] == username):
            return user
    return False


def handle_client(client, addr):
    global clients
    print(f"[NEW CONNECTION] {addr} connected")
    # connection by client
    while True:
        # recieve REQ
        MSG = client.recv(1024)
        MSG = recv_repr(MSG)
        # handle REQ
# USER ------------------------------------------------------------------
        if(MSG['request'] == CHECK_USER_REQ['request']):
            result = users.check_username(MSG['username'])
            if(result != False):
                username = result['username']

                # -------------------------------
                if(MSG['content'] == '-find'):
                    CHECK_USER_FIND_RES['content'] = True

                    CHECK_USER_FIND_MSG = send_repr(CHECK_USER_FIND_RES)
                    client.send(CHECK_USER_FIND_MSG)

                # -------------------------------
                if(MSG['content'] == '-online'):
                    result = check_online_user(username)
                    if(result != False):
                        CHECK_USER_ONLINE_RES['content'] = True
                    else:
                        CHECK_USER_ONLINE_RES['content'] = False

                    CHECK_USER_ONLINE_MSG = send_repr(
                        CHECK_USER_ONLINE_RES)
                    client.send(CHECK_USER_ONLINE_MSG)

                # -------------------------------
                if(MSG['content'] == '-show_date'):
                    SHOW_DOB_RES['dob'] = result['dob']
                    SHOW_DOB_MSG = send_repr(SHOW_DOB_RES)
                    client.send(SHOW_DOB_MSG)

                # -------------------------------
                if(MSG['content'] == '-show_fullname'):
                    SHOW_NAME_RES['fullname'] = result['fullname']
                    SHOW_NAME_MSG = send_repr(SHOW_NAME_RES)
                    client.send(SHOW_NAME_MSG)

                # -------------------------------
                if(MSG['content'] == '-show_note'):
                    SHOW_NOTE_RES['note'] = result['note']
                    SHOW_NOTE_MSG = send_repr(SHOW_NOTE_RES)
                    client.send(SHOW_NOTE_MSG)

                # -------------------------------
                if(MSG['content'] == '-show_all'):
                    SHOW_ALL_RES_COPY = copy_DATA(SHOW_ALL_RES, result)
                    SHOW_ALL_MSG = send_repr(SHOW_ALL_RES_COPY)
                    client.send(SHOW_ALL_MSG)

            else:
                if(MSG['content'] == '-find'):
                    CHECK_USER_FIND_RES['content'] = False
                    CHECK_USER_FIND_MSG = send_repr(CHECK_USER_FIND_RES)
                    client.send(CHECK_USER_FIND_MSG)
                else:
                    CHECK_USER_RES['content'] = False
                    CHECK_USER_MSG = send_repr(CHECK_USER_RES)
                    client.send(CHECK_USER_MSG)

# SETUP ------------------------------------------------------------------
        if(MSG['request'] == SET_UP_REQ['request']):
            if(MSG['content'] == '-fullname'):
                users.update_fullname(MSG['username'], MSG['change_value'])

            if(MSG['content'] == '-date'):
                users.update_dob(MSG['username'], MSG['change_value'])

            if(MSG['content'] == '-note'):
                users.update_note(MSG['username'], MSG['change_value'])

            SET_UP_RES['content'] = True
            SET_UP_MSG = send_repr(SET_UP_RES)
            client.send(SET_UP_MSG)

# CHANGE_PASSWORD -------------------------------------------------------
        if(MSG['request'] == CHECK_PASSWORD_REQ['request']):

            if(MSG['cryptography'] == True):
                MSG['password'] = decrypt_str(MSG['password'])
                CHECK_PASSWORD_RES['cryptography'] = True
            else:
                CHECK_PASSWORD_RES['cryptography'] = False

            result = users.check_username_password(
                MSG['username'], MSG['password'])
            if (result != False):
                CHECK_PASSWORD_RES['content'] = True
                CHECK_PASSWORD_MSG = send_repr(CHECK_PASSWORD_RES)
                client.send(CHECK_PASSWORD_MSG)
            else:
                CHECK_PASSWORD_RES['content'] = False
                CHECK_PASSWORD_MSG = send_repr(CHECK_PASSWORD_RES)
                client.send(CHECK_PASSWORD_MSG)

        if(MSG['request'] == CHANGE_PASSWORD_REQ['request']):

            if(MSG['cryptography'] == True):
                MSG['password'] = decrypt_str(MSG['password'])

            users.update_password(MSG['username'], MSG['password'])
            print(f"PASSWORD of {MSG['username']} changed!")

            NOTIFICATION_RES['content'] = "your PASSWORD changed!"
            client.send(send_repr(NOTIFICATION_RES))

# CHAT -----------------------------------------------------------------
        if(MSG['request'] == CHAT_ROOM_REQ['request']):
            list_online_users = []
            for user in online_users:
                if(user["username"] != MSG["username"]):
                    list_online_users.append(user["username"])

            CHAT_ROOM_RES["online_users"] = list_online_users
            CHAT_ROOM_MSG = send_repr(CHAT_ROOM_RES)
            client.send(CHAT_ROOM_MSG)

        if(MSG['request'] == CREATE_ROOM_REQ['request']):
            id_room = MSG['id_room']
            host = MSG["username"]
            customers = MSG["list_user_room"]

            room = {
                "id_room": id_room,
                "users": []
            }

            customers.append(host)

            for user in customers:
                for online_user in online_users:
                    if(user == online_user["username"]):
                        room['users'].append(online_user)
                        CREATE_ROOM_RES["id_room"] = id_room
                        CREATE_ROOM_MSG = send_repr(CREATE_ROOM_RES)
                        online_user['client'].send(CREATE_ROOM_MSG)
            rooms.append(room)

        if(MSG['request'] == CHAT_REQ['request']):
            host = MSG["username"]
            id_room = MSG['id_room']
            content = "[" + host + "]" + " " + MSG['content']
            for room in rooms:
                if(room['id_room'] == id_room):
                    for user in room["users"]:
                        if(user["username"] != host):
                            CHAT_RES['username'] = host
                            CHAT_RES['content'] = content
                            CHAT_MSG = send_repr(CHAT_RES)
                            user["client"].send(CHAT_MSG)

# LOGIN -----------------------------------------------------------------
        if(MSG['request'] == LOGIN_REQ['request']):

            user = {
                "username": str,
                "client": socket.socket,
            }

            if(MSG["cryptography"] == True):
                MSG['password'] = decrypt_str(MSG['password'])

            result = users.check_username_password(
                MSG['username'], MSG['password'])
            if(result != False):
                for key, val in LOGIN_RES.items():
                    if key in result:
                        LOGIN_RES[key] = result[key]

                LOGIN_RES['password'] = ""
                LOGIN_RES['online'] = True
                LOGIN_MSG = send_repr(LOGIN_RES)
                client.send(LOGIN_MSG)

                users.update_online(MSG['username'], True)

                user["username"] = result['username']
                user["client"] = client

                online_users.append(user)
                for user in online_users:
                    user_name = user["username"]
                    print(f"{user_name} is online")

            else:
                LOGIN_MSG = send_repr(FALSE_RES)
                client.send(LOGIN_MSG)


# REGISTER ------------------------------------------------------------------
        if(MSG['request'] == REGISTER_REQ['request']):
            result = users.check_username(MSG['username'])
            if(result == False):
                REGISTER_RES['username'] = MSG['username']
                RESISTER_MSG = send_repr(REGISTER_RES)
                client.send(RESISTER_MSG)
            else:
                RESISTER_MSG = send_repr(FALSE_RES)
                client.send(RESISTER_MSG)

        if(MSG['request'] == DATA_REQ['request']):

            if(MSG['cryptography'] == True):
                MSG['password'] = decrypt_str(MSG['password'])

            DATA = users.copy_info(MSG)
            # insert
            users.insert_info(DATA)


# DISCONNECT ----------------------------------------------------------------
        if(MSG['request'] == DISCONNECT_REQ['request']):
            DISCONNECT_RES['username'] = MSG['username']
            DISCONNECT_MSG = send_repr(DISCONNECT_RES)

            client.send(DISCONNECT_MSG)
            print(f"[{addr[1]}] [{MSG['username']}] {DISCONNECT_REQ['request']}")
            send_all(clients, client, MSG['username'], MSG['request'])

            clients.remove(client)
            client.close()

            online_users.remove(
                {"username": MSG['username'], "client": client})
            users.update_online(MSG['username'], False)
            break

        print(f"[{addr[1]}] {MSG}")


def send_all(clients, client, username, content):
    content = "[" + username + "]" + " " + content
    CHAT_RES['username'] = ""
    CHAT_RES['content'] = content
    MSG = send_repr(CHAT_RES)
    for c in clients:
        if(c != client):
            c.send(MSG)


start()
