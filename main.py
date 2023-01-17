import sys
import sqlite3
from startScreen import login_main


def connect_to_db(db_name):
    return sqlite3.connect(db_name)
    

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please enter a valid database file!!")
    else:
        if len(sys.argv) > 2:
            print("Error usage! Usage:main.py [db_name.db]")
        else:
            if sys.argv[1].endswith(".db"):
                db = connect_to_db(sys.argv[1])
                login_main(db)
            else:
                print("The input file name is not a file name ending in '. db'")


