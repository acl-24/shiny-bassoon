import sqlite3
import time
import uuid


def error_msg(str):
    error_str_line = "\n************************\n"
    print(error_str_line + str + error_str_line)

def info_msg(str):
    info_str_line = "\n-------------------------\n"
    print(info_str_line + str + info_str_line)
    
class userScreen():
    def __init__(self, db, cursor, uid):
        self.db = db
        self.cursor = cursor
        self.uid = uid
        self.session = None
        
        self.songs_search_res = []
        self.artists_search_res = []
        self.songs_page = 0
        self.artists_page = 0
        
        self.main_screen()
    
    def main_screen(self):
        while True:
            if self.session is None:
                print('''
                    ===============User Screen==================
                    |   [1.Search for songs and playlists   ]  |
                    |   [2.Search for artists               ]  |
                    |   [3.Start a session                  ]  |
                    |   [4.Logout                           ]  |
                    ============================================
                    ''')
            else:
                print('''
                    ===============User Screen==================
                    |   [1.Search for songs and playlists   ]  |
                    |   [2.Search for artists               ]  |
                    |   [3.End the session                  ]  |
                    |   [4.Logout                           ]  |
                    ============================================
                    ''')
                
            try:
                option = int(input('Please enter the option you want to choose(1/2/3/4):'))
            except ValueError:
                error_msg("Error: Invalid input")
                option = int(input('Please enter the option you want to choose(1/2/3/4):'))
                
            if option == 1:
                self.search_for_songs_and_playlists()
            elif option == 2:
                self.search_for_artists()
            elif option == 3:
                if self.session is None:
                    self.start_session()
                else:
                    self.end_session()
            elif option == 4:
                self.end_session()
                return
            else:
                error_msg("Error: Invalid input")
                
    def search_for_songs_and_playlists(self):
        print("=====Search for songs and playlists=====")
        text = input("Search text:")
        if len(text) == 0:
            self.songs_search_res = []
            return

        self.songs_page = 0

        keywords = set(text.split(' '))

        where = ''
        order = ''
        for keyword in keywords:
            if keyword == " " or keyword == '':
                continue
            if len(where) != 0:
                where += " or "

            where += u"title like \'%{}%\'".format(keyword)
            if len(order) != 0:
                order += " + "

            order += u"case when title like \'%{}%\' then 1 else 0 end".format(keyword)

        if len(where) == 0 or len(order) == 0:
            return
        sql = u"select sid, null as pid, title, duration, null as uid, " + order + " as orderNum from songs where " \
              + where + " union all select null as sid, pid, title, null as duration, uid,  " + order + \
              " as orderNum from playlists where " + where + " order by orderNum desc"
        self.cursor.execute(sql)
        self.songs_search_res = self.cursor.fetchall()
        if len(self.songs_search_res) == 0:
            error_msg("No result!")
            return
        
        items = []
        for item in self.songs_search_res:
            if item[1] is None and item[0] is not None:
                song = Song(self)
                song.id = item[0]
                song.title = item[2]
                song.duration = item[3]
                items.append(song)

            if item[0] is None and item[1] is not None:
                playlist = PlayList(self)
                playlist.id = item[1]
                playlist.title = item[2]
                sql = "select sum(duration) from plinclude left join songs on plinclude.sid=songs.sid " \
                      "where plinclude.pid='" + str(item[1]) + "'"

                self.cursor.execute(sql)
                res = self.cursor.fetchall()
                playlist.total_duration = res[0][0]
                items.append(playlist)

        if len(self.songs_search_res) % 5 == 0:
            self.songs_page = int(len(self.songs_search_res) / 5)
        else:
            self.songs_page = int(len(self.songs_search_res) / 5) + 1
        
        p = 0
        current_page = []
        while True:
            current_page = []
            print("==========Search Result==========")
            for item in items[p*5: (p+1)*5]:
                print(item)
                current_page.append(item)
            print('''
                  ==============options=============
                  |   [1.Previous page        ]    |
                  |   [2.Next page            ]    |
                  |   [3.Select               ]    |
                  |   [4.Back                 ]    |
                  ==================================
                  ''')

            option = int(input("Enter your choice(1/2/3/4)"))
            
            if option == 1:
                if p == 0:
                    error_msg("No before page")
                else:
                    p -= 1
                    continue
            elif option == 2:
                if p == self.songs_page - 1:
                    error_msg("No after page")
                else:
                    p += 1
            elif option == 3:
                select = int(input("Enter the index of the item you want to choose(1-5)"))
                if select>len(current_page) or select<=0:
                    error_msg("Error: Invalid input")
                else:
                    current_page[select-1].action()
            elif option == 4:
                return
            else:
                error_msg("Error: Invalid input")
        
    def search_for_artists(self):
        print("========Search for artists========")
        text = input("Search text:")
        if len(text) == 0:
            self.artists_search_res = []
            return
        
        self.artists_page = 0

        keywords = set(text.split(' '))

        order_name = ''
        order_title = ''
        for keyword in keywords:
            if keyword == " " or keyword == '':
                continue
            if len(order_name) != 0:
                order_name += " + "

            order_name += u"case when name like \'%{}%\' then 1 else 0 end".format(keyword, keyword)
            if len(order_title) != 0:
                order_title += " + "

            order_title += u"case when title like \'%{}%\' then 1 else 0 end".format(keyword, keyword)

        if len(order_name) == 0 or len(order_title) == 0:
            return
              
        sql = u"select aid, name, nationality, sum(score) from(" \
            "select artists.aid as aid, name, nationality, sum(" + order_title + ") as score " \
            "from artists left join perform on artists.aid=perform.aid left join songs on perform.sid=songs.sid group by artists.aid " \
            "union all select aid, name, nationality, " + order_name + " from artists) group by aid order by score desc"
        self.cursor.execute(sql)
        self.artists_search_res = self.cursor.fetchall()
        
        if len(self.artists_search_res) == 0:
            error_msg("No result!")
            return
        
        items = []
        for item in self.artists_search_res:
            artist = Artist(self)
            artist.id = item[0]
            artist.name = item[1]
            artist.nationality = item[2]
            
            sql = u"select count(aid) from perform where aid='{}'".format(item[0])
            self.cursor.execute(sql)
            artist.songs_num = self.cursor.fetchall()[0][0]
            
            items.append(artist)

        if len(self.artists_search_res) % 5 == 0:
            self.artists_page = int(len(self.artists_search_res) / 5)
        else:
            self.artists_page = int(len(self.artists_search_res) / 5) + 1
        
        p = 0
        current_page = []
        while True:
            current_page = []
            print("==========Search Result==========")
            for item in items[p*5: (p+1)*5]:
                print(item)
                current_page.append(item)
            print('''
                  ==============options=============
                  |   [1.Previous page        ]    |
                  |   [2.Next page            ]    |
                  |   [3.Select               ]    |
                  |   [4.Back                 ]    |
                  ==================================
                  ''')

            option = int(input("Enter your choice(1/2/3/4)"))
            
            if option == 1:
                if p == 0:
                    error_msg("No before page")
                else:
                    p -= 1
                    continue
            elif option == 2:
                if p == self.songs_page - 1:
                    error_msg("No after page")
                else:
                    p += 1
            elif option == 3:
                select = int(input("Enter the index of the item you want to choose(1-5)"))
                if select>len(current_page) or select<=0:
                    error_msg("Error: Invalid input")
                else:
                    current_page[select-1].action()
            elif option == 4:
                return
            else:
                error_msg("Error: Invalid input")
        
        
        
    def start_session(self):
        self.session = Session(self.uid)
        
    def end_session(self):
        if self.session is not None:
            print('''
                  ====Are you sure end the session?====
                  |   [1.Confirm                 ]    |
                  |   [2.Cancel                  ]    |
                  =====================================
                  ''')
            ok = int(input("Please enter your choice(1/2)"))
            if ok == 1:
                self.session.end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                sql = "insert into sessions values ('{}', '{}', '{}', '{}')".format(self.session.uid,
                                                                                    self.session.session_num,
                                                                                    self.session.start_time,
                                                                                    self.session.end_time)
                self.cursor.execute(sql)
                self.db.commit()
                self.session = None
            elif ok == 2:
                return
            else:
                error_msg("Error: Invalid input")

class Session:
    def __init__(self, uid):
        self.session_num = uuid.uuid1().hex
        self.start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.end_time = None
        self.uid = uid


class Song:
    def __init__(self, parent):
        self.parent = parent
        self.type = "song"
        self.id = ''
        self.title = ''
        self.duration = 0
    
    def __str__(self) -> str:
        bar = "-------------------------------------"
        return bar + '\n' \
                    +"Type:" + self.type + '\n' \
                    + "Sid:" + self.id + '\n' \
                    + "Title:" + self.title + '\n' \
                    + "Duration:" + str(self.duration) \
                    + '\n' + bar

    def action(self):
        while True:
            print('''
                    ==============options=============
                    |   [1.listen               ]    |
                    |   [2.Add it to a playlist ]    |
                    |   [3.Get more information ]    |
                    |   [4.Back                 ]    |
                    ==================================
                    ''')
            option_for_song = int(input("Enter your choice(1/2/3):"))
            if option_for_song == 1:
                if self.parent.session is None:
                    self.parent.start_session()

                sql = u"select cnt from listen where uid=" + self.parent.uid + " and sno='" + self.parent.session.session_num\
                    + "' and sid='" + self.id + "'"
                self.parent.cursor.execute(sql)
                res = self.parent.cursor.fetchall()

                if len(res) == 0:
                    sql = u"insert into listen values('{}', '{}', '{}', 1)".format(self.parent.uid,
                                                                                self.parent.session.session_num,
                                                                                self.id)
                    self.parent.cursor.execute(sql)
                    self.parent.db.commit()
                else:
                    cnt = res[0][0] + 1
                    sql = u"update listen set cnt='" + str(int(cnt)) + "' where uid=" + self.parent.uid + " and sno='"\
                        + self.parent.session.session_num + "' and sid='" + self.id + "'"
                    self.parent.cursor.execute(sql)
                    self.parent.db.commit()
            elif option_for_song == 2:
                sql = u"select pid, title from playlists where uid=" + self.parent.uid
                self.parent.cursor.execute(sql)
                plists = self.parent.cursor.fetchall()

                print("=========select a playlist=========")
                for i in range(len(plists)):
                    print("|   [" + str(i+1) + '.' + plists[i][1])
                
                print("|   [{}.Add to a new playlist\n".format(i+2) + "====================================")
                
                option = int(input("Enter your choice:"))
                if option > i+2 or option <= 0:
                    error_msg("Invalid input")
                    continue
                elif option == i+2:
                    p_title = input("Please enter a new playlist title:")
                    if len(p_title) == 0:
                        error_msg("Error: Playlist title should not be empty")
                        continue
                    else:
                        pid = uuid.uuid1().hex
                    
                    sql = u"insert into playlists values('{}', '{}', '{}')".format(pid, p_title, self.parent.uid)
                    self.parent.cursor.execute(sql)
                    self.parent.db.commit()
                else:
                    p_title = plists[option-1][1]
                    pid = plists[option-1][0]
                    
                sql = u"insert into plinclude values('{}', '{}', '{}')".format(pid, self.id, None)
                
                try:
                    self.parent.cursor.execute(sql)
                    self.parent.db.commit()
                    info_msg("Successfully add song to playlist!")
                except sqlite3.IntegrityError:
                    error_str = self.title + " is already in the playlist:" + p_title
                    error_msg(error_str)
                    continue
            elif option_for_song == 3:
                print("=========Get more information=========")
                print(self)
                sql = u"select name from perform left join artists on perform.aid=artists.aid where sid='{}'".format(self.id)
                self.parent.cursor.execute(sql)
                artists_name = self.parent.cursor.fetchall()
                print("The artists who perform:")
                for name in artists_name:
                    print(name[0])
                print("-------------------------------------")
                sql = u"select title from plinclude left join playlists on plinclude.pid=playlists.pid where sid='{}'".format(self.id)
                self.parent.cursor.execute(sql)
                playlists_title = self.parent.cursor.fetchall()
                print("The playlists the song is in:")
                for title in playlists_title:
                    print(title[0])
                print("-------------------------------------")
                    
            elif option_for_song == 4:
                break


class PlayList:
    def __init__(self, parent):
        self.parent = parent
        self.type = "playlist"
        self.id = ''
        self.title = ''
        self.uid = ''
        self.total_duration = 0
    
    def __str__(self) -> str:
        bar = "-------------------------------------"
        return bar + '\n' \
                    + "Type:" + self.type + '\n' \
                    + "Pid:" + self.id + '\n' \
                    + "Title:" + self.title + '\n' \
                    + "Total Duration:" + str(self.total_duration) \
                    + '\n' + bar

    def action(self):
        while True:
            sql = u"select plinclude.sid, title, duration from plinclude left join songs on plinclude.sid=songs.sid where pid='{}'".format(self.id)
            self.parent.cursor.execute(sql)
            songs = self.parent.cursor.fetchall()
            songs_item = []
            print("=============Playlist=============")
            for song in songs:
                s = Song(self.parent)
                s.id = song[0]
                s.title = song[1]
                s.duration = song[2]
                songs_item.append(s)
                print(s)
            
            print('''
                  ==============options=============
                  |   [1.Select               ]    |
                  |   [2.Back                 ]    |
                  ==================================
                  ''')

            option = int(input("Enter your choice(1/2)"))
            
            if option == 1:
                select = int(input("Enter the index of the item you want to choose:"))
                if select>len(songs_item) or select<=0:
                    error_msg("Error: Invalid input")
                else:
                    songs_item[select-1].action()
            elif option == 2:
                return
            else:
                error_msg("Error: Invalid input")

class Artist():
    def __init__(self, parent) -> None:
        self.parent = parent
        
        self.type = "Artist"
        self.id = ''
        self.name = ''
        self.nationality = ''
        self.songs_num = 0
        
    def __str__(self) -> str:
        bar = "-------------------------------------"
        return bar + '\n' \
                    +"Type:" + self.type + '\n' \
                    + "Name:" + self.name + '\n' \
                    + "Nationality:" + self.nationality + '\n' \
                    + "Songs number:" + str(self.songs_num) \
                    + '\n' + bar
    
    def action(self):
        while True:
            sql = u"select songs.sid, title, duration from perform left join songs on perform.sid=songs.sid where aid='{}'".format(self.id)
            self.parent.cursor.execute(sql)
            songs = self.parent.cursor.fetchall()
            songs_item = []
            print("=========The songs performed by artist==========")
            for song in songs:
                s = Song(self.parent)
                s.id = song[0]
                s.title = song[1]
                s.duration = song[2]
                songs_item.append(s)
                print(s)
            
            print('''
                  ==============options=============
                  |   [1.Select               ]    |
                  |   [2.Back                 ]    |
                  ==================================
                  ''')

            option = int(input("Enter your choice(1/2)"))
            
            if option == 1:
                select = int(input("Enter the index of the item you want to choose:"))
                if select>len(songs_item) or select<=0:
                    error_msg("Error: Invalid input")
                else:
                    songs_item[select-1].action()
            elif option == 2:
                return
            else:
                error_msg("Error: Invalid input")