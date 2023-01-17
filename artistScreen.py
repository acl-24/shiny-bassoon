import sys
import sqlite3
from PyQt5 import QtWidgets

def artistScreen(db, cursor, aid):
    pass

class ArtistScreen(QtWidgets.QWidget):
    def __init__(self, parent, aid, db):
        super(ArtistScreen, self).__init__()

        self.setWindowTitle("Artist Screen")

        self.aid = aid
        self.db = db
        self.parent = parent
        self.cursor = self.db.cursor()

        self.layout = QtWidgets.QGridLayout()

        self.setLayout(self.layout)


