from msilib.schema import Error
import sqlite3
import time

import userScreen
import artistScreen

def error_msg(str):
    error_str_line = "\n************************\n"
    print(error_str_line + str + error_str_line)

def login_main(db):
    cursor = db.cursor()
    while True:
        print('''
            =====System Login======
              |   [1.Login   ]  |
              |   [2.Register]  |
              |   [3.quit    ]  |
            =======================
              ''')
        
        try:
            option = int(input('Please enter the option you want to enter(1/2/3):'))
        except ValueError:
            error_msg("Error: Invalid input")
            option = int(input('Please enter the option you want to enter(1/2/3):'))
        
        if option == 1:
            login(db, cursor)
        elif option == 2:
            register(db, cursor)
        elif option == 3:
            error_msg("Quit successfully!")
            break
        else:
            error_msg("Error: Invalid input")

def login(db, cursor):
    print("=====Login=====")
    username = input("Username:")
    while len(username) == 0:
        error_msg("Error: Username is empty!")
        username = input("Username:")
    password = input("Password:")
    while len(password) == 0:
        error_msg("Error: Password is empty!")
        password = input("Password:")
        
    sql = u"select pwd from users where uid='{}'".format(username)
    try:
        cursor.execute(sql)
        pwd_uid = cursor.fetchall()
    except sqlite3.OperationalError:
        error_msg("Error: Invalid username")
        return

    sql = u"select pwd from artists where aid='{}'".format(username)
    try:
        cursor.execute(sql)
        pwd_aid = cursor.fetchall()
    except sqlite3.OperationalError:
        error_msg("Error: Invalid username")
        return

    if len(pwd_uid) == 0 and len(pwd_aid) == 0:
        error_msg("Error: Id is not exist!")
        return

    if len(pwd_uid) == 0:
        if pwd_aid[0][0] == password:
            artistScreen(db, cursor, username)
            return
        else:
            error_msg("Error password!")
            return

    if len(pwd_aid) == 0:
        if pwd_uid[0][0] == password:
            userScreen(db, cursor, username)
            return
        else:
            error_msg("Error password!")
            return
            
    if pwd_uid[0][0] != password and pwd_aid[0][0] != password:
        error_msg("Error password!")
        return

    if pwd_uid[0][0] == password and pwd_aid[0][0] != password:
        userScreen(db, cursor, username)
        return

    if pwd_aid[0][0] == password and pwd_uid[0][0] != password:
        artistScreen(db, cursor, username)
        return

    if pwd_aid[0][0] == password and pwd_uid[0][0] == password:
        print('''
            =====Select identity===
              |   [1.User    ]  |
              |   [2.Artist  ]  |
            =======================
              ''')
        select = int(input("Select the login identity(1/2):"))
        if select == 1:
            userScreen(db, cursor, username)
            return
        elif select == 2:
            artistScreen(db, cursor, username)
            return
        else:
            error_msg("Error input")
            return
        
def register(db, cursor):
    print("=====Register for user=====")
    username = input("Username:")
    name = input("Name:")
    password = input("Password:")
    
    if len(username) == 0:
        error_msg("Error: Uid is empty")
        return

    if len(password) == 0:
        error_msg("Error: Password is empty")
        return

    if len(name) == 0:
        error_msg("Error: Name is empty")
        return

    sql = u"insert into users values ('{}', '{}', '{}')".format(username, name, password)
    try:
        cursor.execute(sql)
        db.commit()
    except sqlite3.IntegrityError:
        error_msg("Error: Uid is exist")
        return

    print("Successfully! Ready to login")
    time.sleep(1)
    userScreen(db, cursor, username)
