import mongodb
import datetime
import json
from store import *
import online
import os
import ctypes
import stdiomask
from FTP_Cryptography import encrypt_str, decrypt_str

db = mongodb.db
users = mongodb.users


# server ---------------------------------------
def check_username(username):
    check_user = {}
    list_users = users.find({"username": username})  # Thái
    for user in list_users:
        check_user = user
    if (check_user != {}):
        return check_user
    else:
        return False


def check_username_password(username, password):
    check_user = {}
    list_users = users.find({"username": username, "password": password})
    for user in list_users:
        check_user = user
    if (check_user != {}):
        return check_user
    else:
        return False


def update_online(username, status):
    myQuery = {"username": username}
    newValue = {"$set": {"online": status}}
    users.update_one(myQuery, newValue)


def update_password(username, newPassword):
    myQuery = {"username": username}
    newValue = {"$set": {"password": newPassword}}
    users.update_one(myQuery, newValue)


def update_fullname(username, newFullname):
    myQuery = {"username": username}
    newValue = {"$set": {"fullname": newFullname}}
    users.update_one(myQuery, newValue)


def update_dob(username, newDob):
    myQuery = {"username": username}
    newValue = {"$set": {"dob": newDob}}
    users.update_one(myQuery, newValue)


def update_note(username, newNote):
    myQuery = {"username": username}
    newValue = {"$set": {"note": newNote}}
    users.update_one(myQuery, newValue)

# client ------------------------------------------


def register():
    REGISTER_REQ['username'] = input("Enter USERNAME: ")
    return REGISTER_REQ


def info_register(username):
    while True:
        password = stdiomask.getpass("Enter PASSWORD: ")
        password_again = stdiomask.getpass("Enter PASSWORD again: ")
        if(password == password_again):
            pwd = password
            cryptography = input(
                "Do you want to encrypt message before sending? (y/n): ")
            while True:
                if (cryptography == 'y'):
                    DATA_REQ['cryptography'] = True
                    c_pwd = encrypt_str(pwd)
                    DATA_REQ['password'] = c_pwd
                    break
                if (cryptography == 'n'):
                    DATA_REQ['cryptography'] = False
                    DATA_REQ['password'] = pwd
                    break
            DATA_REQ['username'] = username
            DATA_REQ["fullname"] = input("Enter FULLNAME: ")
            DATA_REQ["dob"] = input("Enter your BIRTHDAY: ")
            DATA_REQ["note"] = input("Enter NOTE: ")
            return DATA_REQ
        print("Password not match!")


def copy_info(DATA_MSG):
    DATA['username'] = DATA_MSG['username']
    DATA['password'] = DATA_MSG['password']
    DATA['fullname'] = DATA_MSG['fullname']
    DATA['dob'] = DATA_MSG['dob']
    DATA['note'] = DATA_MSG['note']
    DATA['online'] = DATA_MSG['online']
    DATA['date'] = DATA_MSG['date']
    return DATA


def insert_info(DATA):
    DATA['_id'] = DATA['username']
    users.insert_one(DATA)


def login():
    LOGIN_REQ['username'] = input("Enter USERNAME: ")
    pwd = stdiomask.getpass("Enter PASSWORD: ")
    cryptography = input(
        "Do you want to encrypt message before sending? (y/n): ")
    while True:
        if (cryptography == 'y'):
            LOGIN_REQ['cryptography'] = True
            c_pwd = encrypt_str(pwd)
            LOGIN_REQ['password'] = c_pwd
            break
        if (cryptography == 'n'):
            LOGIN_REQ['cryptography'] = False
            LOGIN_REQ['password'] = pwd
            break
    return LOGIN_REQ


def check_change_password():
    password = stdiomask.getpass("Enter PASSWORD: ")
    cryptography = input(
        "Do you want to encrypt message before sending? (y/n): ")
    pwd = password
    while True:
        if (cryptography == 'y'):
            CHECK_PASSWORD_REQ['cryptography'] = True
            c_pwd = encrypt_str(pwd)
            CHECK_PASSWORD_REQ['password'] = c_pwd
            break
        if (cryptography == 'n'):
            CHECK_PASSWORD_REQ['cryptography'] = False
            CHECK_PASSWORD_REQ['password'] = pwd
            break
    return CHECK_PASSWORD_REQ


def change_password():
    while True:
        password = stdiomask.getpass("new PASSWORD: ")
        password_again = stdiomask.getpass("new PASSWORD again: ")
        if(password == password_again):
            return password
        print("Password not match!")
