# coding=utf8
# from pymysql import Connect,cursors
# from pymysql.err import OperationalError
import pymysql.cursors
import time
import os
import datetime
from fengmaoTest_Tools.txt_read import txtCont
import logging.config
from fengmaoTest_Tools.fengmao_redis import redisInit
from fengmaoTest_Tools.OpenExcel import openExcel

dict = txtCont("../data/baseConfigNew.txt")
host = dict['host']
db = dict['db']
user = dict['user']
password = dict['password']
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
    def dbselect(self,sql):
      with self.connection.cursor() as cursor:
        cursor.execute(sql)
      return cursor.fetchall()
    def dbDelete(self,sql):
      with self.connection.cursor() as cursor:
        cursor.execute(sql)
      self.connection.commit()
    def dbInsert(self,sql):
      # print(sql)
      with self.connection.cursor() as cursor:
        cursor.execute(sql)
      self.connection.commit()
      return str(cursor.lastrowid)
    def dbUpdata(self,sql):
        with self.connection.cursor() as cusor:
            cusor.execute(sql)
        self.connection.commit()
    def close(self):
        self.connection.close()
    def sql_length(self, sql):
        db = DB()
        db_length = db.dbselect(sql)
        j = 0
        for row in db_length:
            j += 1
        return j
    def db_insert_params(self,recordeDict,tableName):
        keysSet = ''
        valueSet = ''
        for i in recordeDict:
            if str(i).lower().find('_time')!=-1:
                recordeDict[i] =  time.strftime("%Y-%m-%d %H:%M:%S")
            if recordeDict[i] !='':
                keysSet = keysSet + ',' + i
                valueSet = valueSet + ',\'' + recordeDict[i]  + '\''
        keysSet = keysSet[1:]
        valueSet = valueSet[1:]
        sql = 'insert into ' + tableName +'(' + keysSet + ')' + ' values(' + valueSet + ')'
        print (sql)
        recordID = self.dbInsert(sql)
        return  recordID
    def insert_bm_order(self,userID,parentUserID,productID,
                                   source_CH,productNum,totalPrice,payMethod,
                                   origPrice,discountAmount,orderDisAmount,
                                   orderStatus,shippingStatus,payStatus,
                        orderType,rechargeType,ransonType,fromOrder):#定义各种类型订单
        if orderType =='2':
            recordeDict = excelFile.getParamByRowID(excelURL, 'bm_order',1)
        elif orderType =='1':
            recordeDict = excelFile.getParamByRowID(excelURL, 'bm_order',int(rechargeType) + 1)
        elif orderType =='4':
            recordeDict = excelFile.getParamByRowID(excelURL,'bm_order',11)
        elif orderType =='8':
            recordeDict = excelFile.getParamByRowID(excelURL,'bm_order',int(ransonType)+ 11)
        else:
            recordeDict = excelFile.getParamByRowID(excelURL,'bm_order',1)
        if orderType !='8':
            productSql = 'select * from up_product where PROD_ID = \'' + productID + '\''
            dbRecorde = self.dbselect(productSql)
            recordeDict['ORDER_NAME'] = dbRecorde[0]['PROD_NAME']
            #print dbRecorde[0]['PROD_NAME']
        recordeDict['USER_ID'] = userID
        #定义ordercode的类型
        #rechargeType = rechargeType #1-话费充值；2-流量充值；3-油卡充值；4-水费充值；5-电费 充值；6-煤气充值；7-游戏点卡充值；8-电影票；9-火车票
        #orderType = orderType #1-充值订单；2-预购订单；3-商品订单；4-提现；5-活动订单；8-冲账订单；9-其他订单
        #order_code_type = '' #1-话费 2-流量 3 预购 4 提现 5 油卡 6 生活缴费 7 虚拟货币 8 电影票 9 火车票 10 服务费 11活动
        if orderType =='2' :
            order_code_type = '3'
        elif orderType =='1' and rechargeType in ['1','2','7','8','9']:
            order_code_type = rechargeType
        elif orderType == '4':
            order_code_type='4'
        elif orderType =='1' and rechargeType == '3':
            order_code_type='5'
        elif  orderType =='1' and rechargeType in ['4','5','6']:
            order_code_type='6'
        elif orderType == '8':
            order_code_type = '10'
        else:
            order_code_type='11'
        recordeDict['ORDER_CODE'] = self.Create_OrderCode(order_code_type)
        #print('生成的ordercode=' +recordeDict['ORDER_CODE'])
        recordeDict['PARENT_USER'] = parentUserID
        recordeDict['PROD_NUMBER'] = productNum
        recordeDict['SOURCE_CH'] = source_CH
        recordeDict['ORIG_PRICE'] = origPrice
        recordeDict['TOTAL_PRICE'] = totalPrice
        recordeDict['DISCOUNT_AMOUNT'] = discountAmount
        recordeDict['ORDER_DISCOUNT_AMOUNT'] = orderDisAmount
        recordeDict['PAY_METHOD'] = payMethod
        recordeDict['ORDER_STATUS'] = orderStatus
        recordeDict['SHIPPING_STATUS'] = shippingStatus
        recordeDict['PAY_STATUS'] = payStatus
        recordeDict['FORMER_ORDER_CODE'] = fromOrder
        recordeDict['RANSOM_TYPE'] = ransonType
        orderList = {}
        # print (recordeDict)
        order_id = self.db_insert_params(recordeDict,'bm_order')
        orderList['ORDER_CODE'] = str(recordeDict['ORDER_CODE'])
        orderList['ORDER_ID'] = str(order_id)
        return orderList
    def insert_train_ticket(self,ORDER_ID,ORDER_CODE,CHANGE_ORDER_CODE,FORMER_TICKET_ID,
                            TRAIN_TYPE,PASSENGER_TYPE,ID_TYPE,SEAT_CLASS,TICKET_PRICE,BUY_FEE,CHANGE_FEE,
                            CHANGE_GAP_FEE,REFUND_FEE,TICKET_STATUS,
                            VALID_STATUS,TICKET_STATUS_DESC,INSURE_PRICE,INSURE_STATUS):
        recordeDict = excelFile.getParamByRowID(excelURL, 'train_ticket', 1)
        recordeDict['ORDER_ID'] = ORDER_ID
        recordeDict['ORDER_CODE'] = ORDER_CODE
        recordeDict['CHANGE_ORDER_CODE'] = CHANGE_ORDER_CODE
        #recordeDict['THIRD_CHANGE_ORDER_CODE'] = THIRD_CHANGE_ORDER_CODE
        recordeDict['FORMER_TICKET_ID'] = FORMER_TICKET_ID
        #recordeDict['TRAIN_NO'] = TRAIN_NO
        recordeDict['TRAIN_TYPE'] = TRAIN_TYPE
        #C-城际高铁；D-动车组；KT-空调特快；KKS-空调快速；KPK-空调普\n\n快；KPM-空调普慢；KS-快速；PK-普快；PM-普慢；
        # XGZ-香港直通车；Z-直达特快；GD-高速动车
        recordeDict['PASSENGER_TYPE'] = PASSENGER_TYPE #1：成人，2：儿童，3：学生
        recordeDict['ID_TYPE'] = ID_TYPE #1：身份证，2：护照，3：台胞证，4：港澳通行证
        recordeDict['SEAT_CLASS'] = SEAT_CLASS #hardseat：硬座，softseat：软座， firstseat：一等座，\n\nsecondseat：
        # 二等座\r\n            ，hardsleeperup：硬卧上铺， hardsleepermid： 硬卧中铺， hardsleeperdown：
        # 硬卧下铺， softsleeperup：\n\n软卧上铺， softsleeperdown：软卧下铺， noseat：无座， businessseat：
        # 商务座， specialseat：特等座， advancedsoftsleeper：高级软卧， \n\notherseat：其他
        recordeDict['TICKET_PRICE'] = TICKET_PRICE
        recordeDict['BUY_FEE'] = BUY_FEE
        recordeDict['CHANGE_FEE'] = CHANGE_FEE
        recordeDict['CHANGE_GAP_FEE'] = CHANGE_GAP_FEE
        recordeDict['REFUND_FEE'] = REFUND_FEE
        recordeDict['TICKET_STATUS'] = TICKET_STATUS
        #1-未出票；2-出票中；3-出票失败；4-出票成功；5-申请改签中；6-改签待确认；\n\n7-支付中；8-支付失败；9-改签中；
        # 10-改签成功；11-退票中；12-退票成功；
        recordeDict['VALID_STATUS'] = VALID_STATUS #1-有效；2-无效；3-废弃
        recordeDict['TICKET_STATUS_DESC'] = TICKET_STATUS_DESC
        recordeDict['INSURE_PRICE'] = INSURE_PRICE
        recordeDict['INSURE_STATUS'] = INSURE_STATUS #1-购保中；2-购保成功；3-购保失败；4-退保中；5-退保成功
        return self.db_insert_params(recordeDict,'train_ticket')
    def insert_bm_payment(self,ORDER_ID,USER_ID,ORDER_CODE,ORDER_AMOUNT,PAY_AMOUNT,DISCOUNT_AMOUNT,
                          PAY_CHN_ID,PAY_CHN,TRADE_TYPE,
                          TRADE_STATUS,SOURCE_CHN,CAN_REFUND_AMOUNT):
        recordeDict = excelFile.getParamByRowID(excelURL, 'bm_payment', 1)
        recordeDict['ORDER_ID'] = ORDER_ID
        recordeDict['USER_ID'] = USER_ID
        recordeDict['ORDER_CODE'] = ORDER_CODE
        recordeDict['ORDER_AMOUNT'] = ORDER_AMOUNT
        recordeDict['PAY_AMOUNT'] = PAY_AMOUNT
        recordeDict['DISCOUNT_AMOUNT'] = DISCOUNT_AMOUNT
        recordeDict['PAY_CHN_ID'] = PAY_CHN_ID
        recordeDict['PAY_CHN'] = PAY_CHN #1：支付宝，2：微信，3：扫呗微信扫码，4：扫呗支付宝扫码',0 猫币支付
        recordeDict['TRADE_TYPE'] = TRADE_TYPE
        recordeDict['TRADE_STATUS'] = TRADE_STATUS
        recordeDict['SOURCE_CHN'] = SOURCE_CHN
        recordeDict['CAN_REFUND_AMOUNT'] = CAN_REFUND_AMOUNT
        return self.db_insert_params(recordeDict,'bm_payment')
    def insert_bm_train_order(self,ORDER_ID,ORDER_CODE,USER_ID,PARENT_ID,PROD_ID,
                              JOURNEY_TYPE,IS_POST,IS_ONLINE,TICKET_MODEL,CHN_ID,ORDER_STATUS,DISCOUNT):
        recordeDict = excelFile.getParamByRowID(excelURL, 'bm_train_order', 1)
        recordeDict['ORDER_ID'] = ORDER_ID
        recordeDict['USER_ID'] = USER_ID
        recordeDict['ORDER_CODE'] = ORDER_CODE
        recordeDict['PARENT_ID'] = PARENT_ID
        recordeDict['PROD_ID'] = PROD_ID
        recordeDict['JOURNEY_TYPE'] = JOURNEY_TYPE
        recordeDict['IS_POST'] = IS_POST
        recordeDict['IS_ONLINE'] = IS_ONLINE #1：支付宝，2：微信，3：扫呗微信扫码，4：扫呗支付宝扫码',0 猫币支付
        recordeDict['TICKET_MODEL'] = TICKET_MODEL
        recordeDict['CHN_ID'] = CHN_ID
        recordeDict['ORDER_STATUS'] = ORDER_STATUS
        recordeDict['DISCOUNT'] = DISCOUNT
        return self.db_insert_params(recordeDict,'bm_train_order')
    def insert_train_amount_change(self,CHANGE_TYPE,ORIG_ORDER_ID,ORIG_ORDER_CODE,USER_ID,
                                   PARENT_ID,LINK_ORDER_CODE,ORDER_CHANGE_AMOUNT,
                                   ORDER_CHANGE_TOTAL_AMOUNT,REWARD_CHANGE_AMOUNT,TICKET_ID,CHANGE_AMOUNT):
        recordeDict = excelFile.getParamByRowID(excelURL, 'train_amount_change', 1)
        recordeDict['CHANGE_TYPE'] = CHANGE_TYPE #变动类型1-购票；2-改签费；3-退票费；4-退保；5-退款
        recordeDict['ORIG_ORDER_ID'] = ORIG_ORDER_ID
        recordeDict['ORIG_ORDER_CODE'] = ORIG_ORDER_CODE
        recordeDict['USER_ID'] = USER_ID
        recordeDict['PARENT_ID'] = PARENT_ID
        recordeDict['LINK_ORDER_CODE'] = LINK_ORDER_CODE
        recordeDict['ORDER_CHANGE_AMOUNT'] = ORDER_CHANGE_AMOUNT
        recordeDict['ORDER_CHANGE_TOTAL_AMOUNT'] = ORDER_CHANGE_TOTAL_AMOUNT #1：支付宝，2：微信，3：扫呗微信扫码，4：扫呗支付宝扫码',0 猫币支付
        recordeDict['REWARD_CHANGE_AMOUNT'] = REWARD_CHANGE_AMOUNT
        recordeDict['TICKET_ID'] = TICKET_ID
        recordeDict['CHANGE_AMOUNT'] = CHANGE_AMOUNT
        return self.db_insert_params(recordeDict,'train_amount_change')
    def insert_mem_user(self,mobile,SUB_USER_TYPE,PARENT_ID,STATUS):
        if SUB_USER_TYPE =='2':
            recordeDict = excelFile.getParamByRowID(excelURL, 'mem_user', 1)
        elif SUB_USER_TYPE == '3':
            recordeDict = excelFile.getParamByRowID(excelURL, 'mem_user', 2)
        elif SUB_USER_TYPE == '4':
            recordeDict = excelFile.getParamByRowID(excelURL, 'mem_user', 3)
        else:
            recordeDict = excelFile.getParamByRowID(excelURL, 'mem_user', 4)
        recordeDict['LOGIN_ACCOUNT'] = mobile
        recordeDict['BIND_MOBILE'] = mobile
        recordeDict['SUB_USER_TYPE'] = SUB_USER_TYPE
        recordeDict['PARENT_ID'] = PARENT_ID
        recordeDict['STATUS'] = STATUS
        user_id = self.db_insert_params(recordeDict,'mem_user')
        if user_id != None:
            self.dbUpdata('update mem_user set RECOMMEND_CODE = HEX(user_id' +  ') where user_id=\'' + str(user_id) + '\'')
        return user_id
    def Create_OrderCode(self,orderType):#生成订单编码
        #传入订单类型。生成orderCode,订单类型为数字
        yyy = time.strftime("%Y")
        mmm = time.strftime("%m")
        ddd = time.strftime("%d")
        #获取redis中的该类型下的起始编号值的key
        RedisorderCode = "redis_order_code_"+yyy[2:4] + '_' + str(int(mmm)) + '_' + str(int(ddd))
        #orderCode生成规则最后编号的前面的前几位
        orderCode = orderType + str(yyy[2:4]) + str(int(mmm)) + str(int(ddd))
        #获取redis中的编号起始值
        Redis_db = redisInit()
        orderCodeValue = Redis_db.redisGetKey(RedisorderCode+"_"+orderType)
        print ('Rediskey is ' + RedisorderCode+"_"+orderType)
        print ('orderCodeValue is ' + orderCodeValue)
        #如果获取的redis中的起始值存在，则更新id+1，否则插入初始值11112
        if 8>len(orderCodeValue)>0:
            orderCode = str(orderCode) + str(int(orderCodeValue)+1)
            Redis_db.redisSetKey(RedisorderCode+"_"+orderType,str(int(orderCodeValue)+1))
        else:
            orderCode = orderCode + '11111'
            Redis_db.redisSetKey(RedisorderCode+"_"+orderType,'11112')
        print('生成的orderCode = ' + orderCode)
        print('此时的rediscode = ' + RedisorderCode+"_"+orderType )
        return orderCode
    def ReUser_id(self,mobile,usertype):
        #usertype 是数字
        return self.dbselect("SELECT user_id FROM mem_user"
                            " WHERE LOGIN_ACCOUNT = "+"'"+mobile+"'"+" AND SUB_USER_TYPE ="+"'"+usertype+"'"+" ;")[0]['user_id']
if __name__ == '__main__':

    db = DB()
    while 1:
        time.sleep(3)
        sql = ("SELECT * FROM train_ticket WHERE ORDER_CODE = '917730450038' and TICKET_STATUS = 5 AND PASSENGER_TYPE =1")
    #db.dbInsert("INSERT INTO `bm_user_book` ( `USER_ID`, `BOOK_CODE`, `BOOK_BALANCE`, `CREATE_TIME`) VALUES ( (SELECT USER_ID FROM mem_user WHERE SUB_USER_TYPE = 2 AND LOGIN_ACCOUNT = 15999999999), 'INCOME_BOOK', '4000', '2016-11-29 02:30:37');")
        print (db.dbselect(sql))
    # delete = ('delete from mem_user where login_account = "0000001135"')
    # db.dbDelete(delete)
    # Insert = ("INSERT INTO `mem_user` (`USER_ID`, `LOGIN_ACCOUNT`, `BIND_MOBILE`, `EMAIL`, `PASSWORD`, `REG_TYPE`, `USER_TYPE`, `SUB_USER_TYPE`, `PARENT_ID`, `PARENT_STATUS`, `USER_LEVEL`, `PWD_SECURITY_LEVEL`, `LOGIN_SOURCE`, `DEPUTY_LOGIN_ACCOUNT`, `OPEN_ID`, `PORTRAIT_IMG_URL`, `NICK_NAME`, `REAL_STATUS`, `REAL_NAME`, `REG_TIME`, `RECOMMEND_CODE`, `PAY_PASSWORD`, `CITY_CODE`, `COUNTY_CODE`, `STATUS`)\
    # VALUES ('1135', '0000001135', '13794071013', NULL, '96e79218965eb72c92a549dd5a330112', '2', '1', '4', NULL, '1', NULL, NULL, NULL, 'owT3fw2CHzspvdBpazYS0FCHAFiY', 'owT3fw2CHzspvdBpazYS0FCHAFiY', 'http://wx.qlogo.cn/mmopen/icOibfWdYOWkhLNjADBbzM4CDAmfKlE3myMzBmOWMwtJoIoVSWxs0RG8ahAeY6OExXdjr9kqpanxUMYdhYo1wEylnmOcWukKoj/0', 'wing', '1', NULL, '2016-06-23 13:46:36', '46F111', NULL, NULL, NULL, '1');")
    # db.dbInsert(Insert)
    # db.dbUpdata('UPDATE mem_user SET PARENT_STATUS = 3  '
    #             'WHERE LOGIN_ACCOUNT = "15700000000" AND SUB_USER_TYPE =2')
    # db.close()
    #性能测试时往数据库插测试数据，并且将订单号写入txt文件。请勿删除以下代码
    # f = open('../data/sqlOrderCode.txt')
    # # print type(f)
    # line = f.readline()
    # f.close()
    # print line[-1]
    # start_orderCode =1117712782051
    # print start_orderCode
    # for i in range(0,1000):
    #     start_orderCode = start_orderCode+1
    #     insert_1="INSERT INTO `bm_order`(`ORDER_CODE`, `OP_ID`, `USER_VISIBLE`, `ORDER_NAME`, `SALES_ID`, `PARENT_USER`, `SOURCE_CH`,\
    #                `USER_ID`, `ORDER_TYPE`, `ORIG_PRICE`, `TOTAL_PRICE`, `DISCOUNT_AMOUNT`, `ORDER_DISCOUNT_AMOUNT`,\
    #                `PROD_NUMBER`, `PAY_METHOD`, `ORDER_STATUS`, `SHIPPING_STATUS`, `PAY_STATUS`, `PAY_TIME`, `CREATE_TIME`,\
    #                `CONFIRM_TIME`, `FROM_AD`, `REFERER`, `ORDER_NOTES`, `PAY_NOTES`, `RECHARGE_TYPE`, `CARD_NUMBER`,\
    #                `FORMER_ORDER_CODE`, `RANSOM_TYPE`)\
    #     VALUES("+bytes(start_orderCode)+", '0', '1', '三元火车票', '0', '200001', '4', '200003', '5', '3', '3', '0', '0', '1','1', '2', '2', '3', '2017-07-12 10:16:19', '2017-07-12 10:16:14', '2017-07-12 10:16:14', NULL, NULL, NULL,NULL, '0', NULL, '', '0');"
    #     db.dbInsert(insert_1)
    #     file_object = open('../data/sqlOrderCode.txt','a')
    #     file_object.write(bytes(start_orderCode)+'\n')
    #     file_object.close()
    #     time.sleep(0.5)
    # db.close()




