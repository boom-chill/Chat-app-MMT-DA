import datetime
import json

TIME_NOW = datetime.datetime.now().strftime("%c")

DATA = {
    "_id": str,
    "username": str,
    "password": str,
    "fullname": str,
    "dob": str,
    "note": str,
    "online": bool,
    "date": str,
}


# response -----------------------------------------------------
NOTIFICATION_RES = {'content': str, 'response': '!NOTIFICATION'}
FALSE_RES = {"response": "!FALSE"}
LOGIN_RES = {"username": str,
             "password": str,
             "fullname": str,
             "date": str,
             "note": str,
             "online": bool,
             "response": "!COMPLETE"
             }
REGISTER_RES = {"username": str,  "response": "!COMLETE"}
CHAT_RES = {"username": str, "content": str, "response": "!CHAT"}
DATA_RES = {
    "username": str,
    "fullname": str,
    "date": str,
    "note": str,
    "online": True,
    "response": "!DATA_CLIENT"
}

DISCONNECT_RES = {"username": str, "response": "!DISCONNECT"}
CHECK_PASSWORD_RES = {"content": bool, "cryptography": bool,
                      "response": "!CHECK_PASSWORD_COMLETE"}
CHANGE_PASSWORD_RES = {"response": "!CHANGE_PASSWORD_COMPLETE"}

# USERS ----------------------
CHECK_USER_RES = {"content": str,
                  "response": "!CHECK_USER_COMPLETE"}

CHECK_USER_FIND_RES = {"content": bool,
                       "response": "!CHECK_USER_FIND_COMPLETE"}
CHECK_USER_ONLINE_RES = {"content": bool,
                         "response": "!CHECK_USER_ONLINE_COMPLETE"}
SHOW_DOB_RES = {"dob": str, "response": "!SHOW_DOB_COMPLETE"}
SHOW_NAME_RES = {"fullname": str, "response": "!SHOW_NAME_COMPLETE"}
SHOW_NOTE_RES = {"note": str, "response": "!SHOW_NOTE_COMPLETE"}
SHOW_ALL_RES = {"username": str,
                "fullname": str,
                "date": str,
                "dob": str,
                "note": str,
                "online": bool,
                "response": "!SHOW_ALL_COMPLETE"
                }
# SETUP --------------------------
SET_UP_RES = {"content": bool, "response": "!SET_UP_COMPLETE"}
# FILE ----------------------------
UPLOAD_SINGLE_RES = {"content": str}
# CHAT -----------------------------
CHAT_ROOM_RES = {"online_users": [], "response": "!CHAT_ROOM"}
CREATE_ROOM_RES = {"id_room": str, "response": "!OPEN_CHAT_ROOM"}

# REQUEST ------------------------------------------------------
FALSE_REQ = {"request": "!FALSE"}
LOGIN_REQ = {"username": str, "password": str,
             "cryptography": bool, "request": "!LOGIN"}
REGISTER_REQ = {"username": str,  "request": "!REGISTER"}
DATA_REQ = {
    "username": str,
    "password": str,
    "fullname": str,
    "dob": str,
    "note": str,
    "online": False,
    "date": TIME_NOW,
    "cryptography": bool,
    "request": "!MORE_INFO"
}
CHAT_REQ = {"username": str, "id_room": str,
            "content": str, "request": "!CHAT"}

CHECK_ONLINE_REQ = {"username": str, "request": "!CHECK_ONLINE"}
DISCONNECT_REQ = {"username": str, "request": "!DISCONNECT"}
CHECK_PASSWORD_REQ = {"username": str, "password": str,
                      "cryptography": bool, "request": "!CHECK_PASSWORD"}
CHANGE_PASSWORD_REQ = {"username": str, "password": str,
                       "cryptography": bool, "request": "!CHANGE_PASSWORD"}

# USERS ----------------------
CHECK_USER_REQ = {"username": str, "content": str, "request": "!CHECK_USER"}

# SETUP--------------------------
SET_UP_REQ = {"username": str, "content": str,
              "change_value": str, "request": "!SET_UP"}
# FILE --------------------------
FILE_DATA = {
    "-id": str,
    "filename": str,
    "file": b'',
    "size": int,
    "cryptography": bool,
}
INFO_FILE = {"size": int, "cryptography": bool}
# UPLOAD -------------------------
UPLOAD_REQ = {"username": str, "content": str,
              "files": [], "request": "!UPLOAD"}

# DOWNLOAD ------------------------
DOWNLOAD_REQ = {"username": str, "content": str, "cryptography": bool,
                "files": [], "request": "!DOWNLOAD"}

# CHAT -----------------------------
CHAT_ROOM_REQ = {"username": str, "request": "!CHAT_ROOM"}
CREATE_ROOM_REQ = {"username": str, "id_room": str,
                   "list_user_room": [], "request": "!CREATE_ROOM"}

# repear MSG ----------------------------------------------------


def send_repr(MSG):
    MSG = json.dumps(MSG).encode('utf-8')
    return MSG


def recv_repr(MSG):
    MSG = json.loads(MSG.decode('utf-8'))
    return MSG


def copy_DATA(destination, source):
    result = destination
    for key, val in result.items():
        if key in source:
            result[key] = source[key]
    return result
