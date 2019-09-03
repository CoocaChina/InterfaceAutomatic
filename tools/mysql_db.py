# coding=utf8
# from pymysql import Connect,cursors
# from pymysql.err import OperationalError
import time
import pymysql.cursors
from tools.OpenExcel import openExcel
from tools.txt_read import txtCont

dict_config = txtCont("../data/baseConfigNew.txt")
host = dict_config['host']
db = dict_config['db']
user = dict_config['user']
password = dict_config['password']
excelFile = openExcel()
excelURL = '../data/DB_Tbales.xls'


# ======== MySql base operating ===================
class DB:

    def __init__(self):
        try:
            # Connect to the database
            self.connection = pymysql.connect(host=host,
                                              user=user,
                                              password=password,
                                              db=db,
                                              charset='utf8mb4',
                                              cursorclass=pymysql.cursors.DictCursor)
        except pymysql.err.OperationalError as e:
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))

    def dbselect(self, sql_data):
        with self.connection.cursor() as cursor:
            cursor.execute(sql_data)
        return cursor.fetchall()

    def dbDelete(self, sql_data):
        with self.connection.cursor() as cursor:
            cursor.execute(sql_data)
        self.connection.commit()

    def dbInsert(self, sql_data):
        # print(sql)
        with self.connection.cursor() as cursor:
            cursor.execute(sql_data)
        self.connection.commit()
        return str(cursor.lastrowid)

    def dbUpdata(self, sql_data):
        with self.connection.cursor() as cusor:
            cusor.execute(sql_data)
        self.connection.commit()

    def close(self):
        self.connection.close()

    def sql_length(self, sql_data):
        db = DB()
        db_length = db.dbselect(sql_data)
        j = 0
        for row in db_length:
            j += 1
        return j

    def db_insert_params(self, recordeDict, tableName):
        keysSet = ''
        valueSet = ''
        for i in recordeDict:
            if str(i).lower().find('_time') != -1:
                recordeDict[i] = time.strftime("%Y-%m-%d %H:%M:%S")
            if recordeDict[i] != '':
                keysSet = keysSet + ',' + i
                valueSet = valueSet + ',\'' + recordeDict[i] + '\''
        keysSet = keysSet[1:]
        valueSet = valueSet[1:]
        sql = 'insert into ' + tableName + '(' + keysSet + ')' + ' values(' + valueSet + ')'
        print(sql)
        recordID = self.dbInsert(sql)
        return recordID

if __name__ == '__main__':

    db = DB()
    while 1:
        time.sleep(3)
        sql = "select * from sxc_pc.sxc_store_plan where status in (50)"
        print(db.dbselect(sql))
        db.close()
