import json

import pymysql
import logging.config

logging.config.fileConfig("../data/logger.conf")
logger = logging.getLogger("example01")
host = '127.0.0.1'
db = 'sxc_gateway'
user = 'root'
password = 'root'


class api_syn:
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

    def select(self, sql):
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
        return cursor.fetchall()

    def db_updata(self, sql_data):
        with self.connection.cursor() as cusor:
            cusor.execute(sql_data)
        self.connection.commit()

    def api_deal_with(self):
        all_api = self.all_api()
        for api_one in all_api:
            api_define = api_one['api_define']
            # api_define = '{"call":{"methodName":"getColdStorageByQuery",' \
            #              '"interfaceName":"com.sxc.supplychain.coldstoragecore.provider.ColdStorageQueryProvider",' \
            #              '"version":"1.0.0","timeout":"3000"},"request":[{"apiParameterName":"query",' \
            #              '"className":"com.sxc.supplychain.coldstoragecore.param.ColdStorageQueryDTO","type":"object"},' \
            #              '{"apiParameterName":"$userId","type":"Long"}],"response":{"result":"result",' \
            #              '"subCode":"subCode","success":"result","errorCode":"errorCode"}} '
            # print(api_one)
            api_define_dict = json.loads(api_define)
            if api_define_dict['call']. __contains__('version'):
                api_define_dict['call']['version'] = '1.0.0.test'
                print(api_define_dict)
                sql_date = "update sxc_gateway_api set api_define = "+"'"+str(json.dumps(api_define_dict))+"'" + "where id = "+str(api_one["id"])+";"
                # print(sql_date)
                self.db_updata(sql_date)

    def all_api(self):
        all_api = self.select('select * from sxc_gateway_api')
        return all_api

if __name__ == '__main__':
    api_syn_test = api_syn()
    #print(api_syn_test.select('select * from sxc_gateway_api'))
    print(api_syn_test.api_deal_with())
