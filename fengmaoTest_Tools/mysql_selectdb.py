#?/bin/usr/python
#-*- coding: utf-8 -*-
import unittest
import os,sys
import logging.config
from fengmaoTest_Tools.mysql_db import DB
    # 获取日志配置文件
logging.config.fileConfig("../data/logger.conf")
logger = logging.getLogger("example01")
class fengmao_selectDB():

  def sql_data_verification(self,sql,ordercode):
    database = DB()
    data = database.dbselect(sql)
    j = 0
    for row in data:
      j+=1
    if j == 1 :
        logging.info ('数据生成正确')
        return data
    else:
        logging.error ('数据生成错误%s',ordercode)
        return None
    database.close()
  def db_bm_order(self,sql):
    db=DB()
    dbbm_order = db.dbselect(sql)
    #print dbbm_order    
    j = 0
    for row in dbbm_order:
      j+=1
    if j == 1 :
        print('订单表数据生成正确')
        return 'checkpass'
    else:
        print('订单表数据生成错误')
        return 'checkfail'
    db.close()
  def db_bm_recharge_order(self,sql,ordercode):
    db1 = DB()
    bm_recharge_order_result = db1.dbselect(sql)
    #print bm_recharge_order_result
    #print sql
    if not bm_recharge_order_result is None:
        i = 0
        for row in bm_recharge_order_result:
          i+=1
          #print row
        #print i
        if i == 1 :
            print('充值订单表数据生成正确')
            return 'checkpass'
        else:
          print ('bm_recharge_order ErrorOrderCode:%s',ordercode)
          return 'checkfail'
        db.close()
  def db_bm_user_book(self,sql,ordercode):
    db = DB()
    dbuser_book_result = db.dbselect(sql)
      #print dbuser_book_result
    if not dbuser_book_result is None:
        num1 = dbuser_book_result[0]['BOOK_BALANCE']
        num2 = dbuser_book_result[0]['BEFORE_CHANGE_BALANCE']
        if num2 - num1 == 100:
          print('bm_user_book_record生成数据正确')
          return 'checkpass'
        else:
          print ('bm_user_book_record and bm_user_book ErrorOrderCode:%s',ordercode)
          return 'checkfail'
    db.close()
  def db_bm_payment(self,sql,ordercode):
    db3 = DB()
    dbbm_payment_result = db3.dbselect(sql)
    if not dbbm_payment_result is None:
        i = 0
        for row in dbbm_payment_result:
          i+=1
        if i == 1 :
            print('bm_payment支付表数据生成正确')
            return 'checkpass'
        else:
          print('bm_payment ErrorOrderCode:%s',orderCode)
          return 'checkfail'
    db3.close()
  def db_bm_not_settle(self,sql,orderCode):
    db6 = DB()
    bm_not_settle_checkresult = db6.dbselect(sql)
    #print bm_not_settle_checkresult
    if not bm_not_settle_checkresult is ():
      print('回调之后冻结表和订单表数据正确')
      return 'checkpass'
    else:
      print ('bm_not_settle and bm_order data is ERROR ordercode:%s',orderCode)
      return 'checkfail'
    db6.close()
  def db_sql(self,sql):
      mysql_DB = DB()
      return mysql_DB.dbselect(sql)
if __name__=='__main__':
    test1 = fengmao_selectDB()
    print(test1.db_sql('SELECT * FROM bm_user_book_record br1 LEFT JOIN bm_order br2 ON br1.ORDER_ID = br2.ORDER_ID WHERE br2.ORDER_CODE = "317615450026";'))





