import os
import sqlite3
from config import dir_path , db_name

class DBHelper():
    def __init__(self):
        self.dbname = dir_path + db_name
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
    def setup(self):
        os.popen(f'touch "{dir_path+db_name}"')
        stmt = 'CREATE TABLE IF NOT EXISTS personals (chat_id INTEGER)'
        self.conn.execute(stmt)
        self.conn.commit()
    def NewUser(self,chat_id):
        stmt = 'SELECT chat_id FROM personals'
        personals = [x[0] for x in self.conn.execute(stmt)]
        return True if chat_id not in personals else False
    def AddNewUser(self,chat_id):
        if self.NewUser(chat_id):
            ban = 0
            stmt = 'INSERT INTO personals (chat_id,ban) VALUES (?,?)'
            args = (chat_id,ban,)
            self.conn.execute(stmt,args)
            self.conn.commit()
    def NumberOfUsers(self):
        stmt = 'SELECT chat_id FROM personals'
        return len([x[0] for x in self.conn.execute(stmt)])
    def BanStatus(self,chat_id):
        stmt = 'SELECT ban FROM personals WHERE chat_id=(?)'
        args = (chat_id,)
        return [x[0] for x in self.conn.execute(stmt,args)][0]
    def Ban(self,chat_id):
        stmt = 'UPDATE personals SET ban=1 WHERE chat_id=(?)'
        args = (chat_id,)
        self.conn.execute(stmt,args)
        self.conn.commit()
    def Unban(self,chat_id):
        stmt = 'UPDATE personals SET ban=0 WHERE chat_id=(?)'
        args = (chat_id,)
        self.conn.execute(stmt,args)
        self.conn.commit()

