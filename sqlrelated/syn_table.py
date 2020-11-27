import pymysql
from pymysql.cursors import DictCursor

from tools.mysql_db import DB
from tools.smtp_base import email
import logging
import logging.config

logging.config.fileConfig("../data/logger.conf")
logger = logging.getLogger("example01")
host = 'rm-bp1enc0yrzt3zu60do.mysql.rds.aliyuncs.com'
db = 'sxc'
user = 'sxc_test'
password = 'Songxiaocai2015'

class syn_mysql():

    def __init__(self):
        self.selectDB = DB()
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

    def select(self, sql):
        with self.connection.cursor(DictCursor) as cursor:
            cursor.execute(sql)
        return cursor.fetchall()

    def syn_script(self, database_name):
        """
        :param database_name: 数据库名称
        :return: 表的创建脚本
        """
        table_list = self.table_comparison(database_name)
        # table_list = ['wechat_dialog']
        for table in table_list:
            # print(table)
            table_name = table
            # 获取创建脚本
            create_tab_script = self.select('show create table ' +database_name+'.'+str(table_name) + ';')
            print(create_tab_script[0]['Create Table'])
            # self.selectDB.connection.cursor().execute(create_tab_script[0]['Create Table'])
            # self.selectDB.connection.commit()

    def table_comparison(self, table1):
        soure_table_list = []
        aim_table_list = []
        soure_table = self.select("select table_name from information_schema.tables where table_schema="+"'"+str(table1)+"';")
        aim_table = self.selectDB.dbselect("select table_name from information_schema.tables where table_schema="+"'" + str(table1) + "';")

        for desc in soure_table:
            soure_table_list.append(desc['table_name'])
        for aim_desc in aim_table:
            aim_table_list.append(aim_desc['table_name'])
        # print(set(soure_table_list).difference(set(aim_table_list)))
        return set(soure_table_list).difference(set(aim_table_list))


if __name__ == '__main__':
    syn_mysql_test = syn_mysql()
    syn_mysql_test.syn_script('sxc_ic')
    syn_mysql_test.selectDB.close()
    print('1111')

