#?/bin/usr/python
#-*- coding: utf-8 -*-
import json
import random

import requests
import os, sys

from fengmaoTest_interface.API_appPayResult import API_appPayResult

sys.path.append("../fengmaoTest_interface")
import time
import logging
import logging.config
import datetime
from copy import deepcopy
from fengmaoTest_Tools.fengmao_md5 import md5encryption
from fengmaoTest_Tools.fengmao_md5 import oldMd5sign
from fengmaoTest_Tools.mysql_db import DB
from fengmaoTest_Tools.OpenExcel import openExcel
from fengmaoTest_Tools.httpRequest import httpRequest
from fengmaoTest_interface.API_getAuthCode import general_getAuthCode
from fengmaoTest_Tools.http_request import http_req
from fengmaoTest_Tools.fengmao_redis import *
from fengmaoTest_Tools import fengmao_Global

    # 获取日志配置文件
logging.config.fileConfig("../data/logger.conf")
logger = logging.getLogger("example01")

class fengmaoAPI_method:
    fengmao_Global._init()
    baseConfig = openExcel()
    http_request = http_req()
    Mysql_db = DB()
    def payment_new(self,appType,mobile,prod_code,caseID):
        db = DB()
        sql_del_poundage = "delete from bm_pay_chn_poundage_config WHERE BUSI_TYPE = '2';"
        sql_ins_poundage_1 = "INSERT INTO `bm_pay_chn_poundage_config` VALUES (NULL, '7', '2', '1', '1', '100', '100');"
        sql_ins_poundage_2 = "INSERT INTO `bm_pay_chn_poundage_config` VALUES (NULL, '8', '2', '1', '1', '100', '100');"
        db.dbDelete(sql_del_poundage)
        db.dbInsert(sql_ins_poundage_1)
        db.dbInsert(sql_ins_poundage_2)
        pay_result = API_appPayResult()
        redis = redisInit()
        logging.config.fileConfig("../data/logger.conf")
        logger = logging.getLogger("example01")
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S")
        httpreq = fengmaoAPI_method()
        interName = 'payment'
        excelURL = '../data/TestData_Xudp.xls'
        baseConfig = openExcel()
        dict = txtCont("../data/baseConfigNew.txt")
        self.reqURL = "http://" + dict["apiurl_test"]
        redisData = redisInit()
        # sql_update_poundage = "update bm_pay_chn_poundage_config set POUNDAGE_VALUE ='100' WHERE BUSI_TYPE = '2'"
        # db.dbUpdata(sql_update_poundage)
        caseParam = baseConfig.getParamByCaseID(excelURL,interName,'1')
        caseParam['prodCode'] = prod_code
        caseParam['appType'] = appType
        method = fengmaoAPI_method()
        submitTime = time.strftime("%Y%m%d%H%M%S")
        caseParam['submitTime'] = submitTime
        caseParam['mobile'] = mobile
        caseParam['payAmount'] = '10'
        method.newUserLogin(caseParam)
        secret = fengmao_Global.get_value('secret')
        appSessionID = str(fengmao_Global.get_value('appSessionID'))
        response = self.http_request.http_req_type(caseParam,interName, '0')
        pay_result.appPayResult(response['result']['orderCode'], appSessionID, secret, '1')
        time.sleep(2)

    def payment(self,APIdicparam):
        baseConfig = openExcel()
        #获取测试域名
        baseUrl = baseConfig.openTxtFile("../data/baseConfig.txt")
        #定义接口参数
        merchant_indexInterface = "d-app/API/payment?"
        #登录获取sessionID和secret
        loginDic = []
        loginResult = fengmaoAPI_method()
        loginDic['appType'] = APIdicparam['appType']
        loginDic['mobile'] = APIdicparam['appType']
        loginDic['passWord'] = APIdicparam['passWord']
        appSessionID = loginResult.newUserLogin(APIdicparam['mobile'], APIdicparam['apptype'])['result'][0]['sessionId']
        secret = loginResult.newUserLogin(APIdicparam['mobile'], APIdicparam['apptype'])['result'][0]['secret']
        #签名需要的参数
        dicparam = {'submitTime': APIdicparam['submitTime'],
                    'appVersion': APIdicparam['appVersion'],
                    'appType': APIdicparam['appType'],
                    'osname': APIdicparam['osname'],
                    'accPayAmount':APIdicparam['accPayAmount'],
                    'cardId':APIdicparam['cardId'],
                    'cardNumber':APIdicparam['cardNumber'],
                    'lifeParams':APIdicparam['lifeParams'],
                    'payAmount':APIdicparam['payAmount'],
                    'payPwd':APIdicparam['payPwd'],
                    'payType':APIdicparam['payType'],
                    'prodCode':APIdicparam['prodCode'],
                    'prodNum':APIdicparam['prodNum'],
                    'unitId':APIdicparam['unitId']}
        sign = md5encryption(dicparam, secret)
        #请求url
        httpResult = httpRequest()
        r = httpResult.HttpGetRequest(baseUrl, merchant_indexInterface, dicparam, appSessionID, sign)
        result = r.json()
        logger.info(r.text)
        if result['success'] == True:
            orderCode = result['result']['orderCode']
            logger.info(result['result']['orderCode'])
            logger.info('payment接口请求成功')
            return result
        else:
            logger.info('接口请求失败')
    def order_confirm(self,caseParamData):
        #代购模式
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        while 1:
            if fengmao_Global.get_value('mobile') != '':
                dicTrain_Value = self.train_query_findTrainByStation(caseParamData)
                #拼接下单的json数据
                #1人下单
                internfaceName = 'order/confirm'
                fname = ("../data/TestData_shijf.xls")
                sheetName = ("API_order_confirm")
                #获取基本接口数据
                caseParam = self.baseConfig.getParamByCaseID(fname, sheetName, '1')
                #更改参数
                caseParam['submitTime'] = time.strftime("%Y%m%d%H%M%S")
                caseParam['appType'] = fengmao_Global.get_value('appType')
                if caseParam['appType'] == 'M':
                    caseParam['prodCode'] = 'Train_custom_C'
                else:
                    caseParam['prodCode'] = 'Train_custom_D'
                caseParam['trainParams'] ={
                                            "trainNo": "G7331",
                                            "contactInfo": {
                                                "cellphone": "15757185534",
                                                "person": "15757185534"
                                            },
                                            "fromStation": "余杭",
                                            "trainDate": "20170816",
                                            "isProduction": 0,
                                            "isOnLine": 1,
                                            "passengers": [
                                                {
                                                    "passengerType": 1,
                                                    "preferenceFromStation": "",
                                                    "schoolCode": "",
                                                    "insureCount": "0",
                                                    "sex": 1,
                                                    "admissionYear": "",
                                                    "studentNo": "",
                                                    "provinceCode": "33",
                                                    "passengerName": "施继峰",
                                                    "insurePrice": "0",
                                                    "eductionalSystem": 0,
                                                    "preferenceToStation": "",
                                                    "idCard": "330184199305203512",
                                                    "contactId": 2,
                                                    "birthday": "1993-05-20",
                                                    "insurNo": "",
                                                    "ticketPrice": "9.1",
                                                    "idType": 1,
                                                    "seatClass": "secondseat"
                                                }
                                            ],
                                            "queryKey": "a838b9f72d7be556a4a882edc451e995",
                                            "ticketModel": 0,
                                            "token": "",
                                            "trainClass": "GD",
                                            "isPost": 0,
                                            "postalId": 0,
                                            "journeyType": 1,
                                            "toStation": "杭州东",
                                            "acceptNoSeat": 0
                                        }
                #所有车票价格
                caseParam['orderAmount'] = str(float(dicTrain_Value['buyFee'])+float(dicTrain_Value['price'])*len(caseParam['trainParams']['passengers']))
                #将默认的请求车票数据更改为新的。以下只更改车票信息。不更改乘客信息
                for trainKEY in dicTrain_Value:
                    for trainJson in caseParam['trainParams']:
                        if trainKEY == trainJson:
                            caseParam['trainParams'][trainJson] = dicTrain_Value[trainKEY]
                #获取乘客列表
                passengerDic = self.train_contact_findList()
                #time.sleep(3)
                while 1:
                    if len(caseParam['trainParams']['passengers']) < int(caseParamData['passengerNum']):
                        dicPassenger = deepcopy(caseParam['trainParams']['passengers'][0])
                        caseParam['trainParams']['passengers'].append(dicPassenger) # 多个乘客时需要增加乘客位置
                        logging.info(caseParam)
                    else:
                        break
                adultDic=[]
                childDic=[]
                for x in range(0,len(passengerDic)):#提取成人乘客信息
                    if passengerDic[x]['passengerType'] == 1:
                        adultDic.append(passengerDic[x])
                    elif passengerDic[x]['passengerType'] == 2:
                        childDic.append(passengerDic[x])
                for i in range(0,int(caseParamData['adult'])):#提起儿童乘客信息
                    caseParam['trainParams']['passengers'][i]['ticketPrice'] = str(
                        float(dicTrain_Value['buyFee']) + float(dicTrain_Value['price']))  # 更新单张票价
                    if adultDic[i]['passengerType'] == 1:
                        for passengKEY in caseParam['trainParams']['passengers'][i]:
                            #print(caseParam['trainParams']['passengers'][i])
                            if adultDic[i].__contains__(passengKEY):  # 判断这个字典里面是否存在这个key
                                caseParam['trainParams']['passengers'][i][passengKEY] = adultDic[i][passengKEY]
                                #print(caseParam['trainParams']['passengers'][i][passengKEY])
                            if dicTrain_Value.__contains__(passengKEY):
                                caseParam['trainParams']['passengers'][i][passengKEY] = dicTrain_Value[passengKEY]
                for j in range(0,int(caseParamData['child'])):
                    caseParam['trainParams']['passengers'][j]['ticketPrice'] = str(
                        float(dicTrain_Value['buyFee']) + float(dicTrain_Value['price']))  # 更新单张票价
                    if childDic[j]['passengerType'] == 2:
                        for passengKEY in caseParam['trainParams']['passengers'][j]:
                            # print(caseParam['trainParams']['passengers'][i])
                            if childDic[j].__contains__(passengKEY):  # 判断这个字典里面是否存在这个key
                                caseParam['trainParams']['passengers'][j][passengKEY] = childDic[j][passengKEY]
                                # print(caseParam['trainParams']['passengers'][i][passengKEY])
                            if dicTrain_Value.__contains__(passengKEY):
                                caseParam['trainParams']['passengers'][j][passengKEY] = dicTrain_Value[passengKEY]
                #更改接受短信的手机号
                caseParam['trainParams']['contactInfo']['cellphone'] = caseParamData['passengerMobile']
                caseParam['trainParams']['contactInfo']['person'] = caseParamData['passengerName']
                # print(caseParam)
                # exit()
                req_json = self.http_request.http_req_type(caseParam, internfaceName, '0')
                if req_json['errCode'] == '10000':
                    dicPaymentInfo={}
                    dicPaymentInfo['orderCode'] = req_json['result']['orderCode']
                    if req_json['result']['discount'] == 0:
                        dicPaymentInfo['discount'] = 1
                    else:
                        dicPaymentInfo['discount']  = float(req_json['result']['discount'] / 10)
                    return dicPaymentInfo
                else:
                    logger.error("下单失败")
    def order_pay(self,caseParamData):#火车票确认支付
        interfaceName = 'order/pay'
        fname = ("../data/TestData_shijf.xls")
        sheetName = ("order_pay")
        sheetName1 = ("train_ticket_case")
        caseparam = self.baseConfig.getParamByCaseID(fname,sheetName,'1')
        #print(caseparam)
        #调用确认订单下单 返回下单的之后的车票订单号码和需要支付的钱
        crteatOrderDic = self.order_confirm(caseParamData)
        caseparam['appType'] = fengmao_Global.get_value('appType')
        caseparam['orderCode'] = crteatOrderDic['orderCode']
        caseparam['payPwd'] = fengmao_Global.get_value('pay_password')
        while 1:#查询确认订单之后的占座结果，如果占座成功就直接支付，如果失败，再次占座
            time.sleep(5)
            orderStatus =self.train_ticket_getOrderStatus(caseparam['orderCode'])['result']['orderstatus']
            if orderStatus == 2:
                orderDtl_result = self.train_ticket_orderDtl(caseparam['orderCode'])
                ticketPirce = 0.0
                for i in (range(0,len(orderDtl_result['result']['ticketList']))):
                    ticketPirce = ticketPirce + float(orderDtl_result['result']['ticketList'][i]['ticketPrice'])+float(orderDtl_result['result']['ticketList'][i]['buyFee'])
                orderAmount = float(orderDtl_result['result']['totalInsurePrice'])+ticketPirce + float(orderDtl_result['result']['payPoundageAmount'])-float(orderDtl_result['result']['orderDiscountAmount'])
                # 插入优惠券
                couponPrice = 0.0
                if caseParamData['couponIds'] == '1':
                    couponPrice = float(orderAmount)*100+100
                    rec_id = self.insert_ECcoupon(fengmao_Global.get_value('user_id'),couponPrice,fengmao_Global.get_value('user_type'))
                elif caseParamData['couponIds'] == '2':
                    couponPrice = float(orderAmount) * 100 - 100
                    rec_id = self.insert_ECcoupon(fengmao_Global.get_value('user_id'), couponPrice,
                                     fengmao_Global.get_value('user_type'))
                elif caseParamData['couponIds'] == '3':
                    couponPrice = float(orderAmount) * 100
                    rec_id = self.insert_ECcoupon(fengmao_Global.get_value('user_id'), couponPrice,
                                     fengmao_Global.get_value('user_type'))
                caseparam['couponIds'] = rec_id
                caseparam['discountAmount'] = couponPrice/100
                # 判断支付方式
                if caseParamData['payType'] == 'MBPAY':
                    if orderAmount<couponPrice/100:
                        caseparam['accPayAmount'] ='0'
                    else:
                        caseparam['accPayAmount'] = orderAmount-couponPrice/100
                else:
                    caseparam['payAmount'] = orderAmount
                    caseparam['payType'] = caseParamData['payType']
                self.http_request.http_req_type(caseparam,interfaceName,'0')
                dicOrder_Info = {}
                while 1:
                    time.sleep(5)
                    Mysql_db = DB()
                    ticketSQL = Mysql_db.dbselect(
                        "SELECT * FROM train_ticket WHERE ORDER_CODE = " + "'" + crteatOrderDic['orderCode'] + "'" + " and TICKET_STATUS = 4 AND PASSENGER_TYPE =1;")
                    Mysql_db.close()
                    if len(ticketSQL) != 0:
                        #print(ticketSQL)
                        dicOrder_Info['ticket_id'] = ticketSQL[0]['TICKET_ID']
                        dicOrder_Info['ticketPrice'] = str(ticketSQL[0]['TICKET_PRICE']/100)
                        dicOrder_Info['orderCode'] = crteatOrderDic['orderCode']
                        return dicOrder_Info
            elif orderStatus == 3:
                crteatOrderDic = self.order_confirm(caseParamData)
                caseparam['orderCode'] = crteatOrderDic['orderCode']
    def train_ticket_applyRefundOrder(self,orderCode):#火车票申请退票接口
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        interfaceName = 'train/ticket/applyRefundOrder'
        fname = ("../data/TestData_shijf.xls")
        sheetName = ("train_ticket_applyRefundOrder")
        caseparam = self.baseConfig.getParamByCaseID(fname,sheetName,'1')
        caseparam['appType'] = fengmao_Global.get_value('appType')
        Refund_tarin_order_list = self.Mysql_db.dbselect("SELECT * FROM train_ticket WHERE ORDER_CODE = "+"'"+orderCode+"'"+" and TICKET_STATUS = 4 ")
        # print(Refund_tarin_order_list)
        if len(Refund_tarin_order_list) != 0:
            for i in range(0,len(Refund_tarin_order_list)):
                caseparam['ticketId'] = Refund_tarin_order_list[i]['TICKET_ID']
                self.http_request.http_req_type(caseparam,interfaceName,'0')
        else:
            exit()
    def train_ticket_orderDtl(self,orderCode):#火车票订单详情接口
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        internfaceName = 'train/ticket/orderDtl'
        caseParam={'submitTime': '20160714090000','appVersion': '2.1.3',
                   'appType':fengmao_Global.get_value('appType'),
                   'osname': 'IOS'}
        caseParam['orderCode'] = orderCode
        req_json = self.http_request.http_req_type(caseParam,internfaceName,'0')
        if req_json['errCode'] == '10000':
            return req_json
        else:
            logger.error('火车票订单详情接口请求失败：%s',orderCode)
    def train_ticket_getOrderStatus(self,orderCode):#获取火车票订单状态
        internfaceName = 'train/ticket/getOrderStatus'
        Contact_param = {'submitTime': '20160714090000', 'appVersion': '2.1.3',
                         'appType': fengmao_Global.get_value('appType'), 'osname': 'IOS',
                         'mobile': fengmao_Global.get_value('mobile'),'orderCode':orderCode}
        req_json = self.http_request.http_req_type(Contact_param, internfaceName, '0')
        return req_json
    def train_ticket_applyChangeTicket(self,caseParamData):#申请改签接口 改签case从申请改签开始
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        interfaceName = 'train/ticket/applyChangeTicket'
        fname = ("../data/TestData_shijf.xls")
        sheetName = ("train_ticket_applyChangeTicket")
        caseparam = self.baseConfig.getParamByCaseID(fname,sheetName,'1')
        caseparam['appType'] = fengmao_Global.get_value('appType')
        caseParamData['orderType'] = '1'
        dicTieketInfo = self.order_pay(caseParamData)
        dicTieketInfo['orderType'] = '2'# dicOrderInfo['orderType']: 1:下单。2：改签
        dicTieketInfo['changeType'] = caseParamData['changeType']# dicOrderInfo['changeType']: 1:低改高。2：平价改。3高改低
        ticketInfo = self.train_query_findTrainByStation(dicTieketInfo)
        for values in ticketInfo:
            if caseparam.__contains__(values):
                caseparam[values] = ticketInfo[values]
        req_json = self.http_request.http_req_type(caseparam,interfaceName,'0')
        if req_json['errCode'] == '10000':
            while True:
                time.sleep(5)
                changeTicketInfo = self.train_ticket_getChangeTicketInfo(dicTieketInfo['ticket_id'])
                ticketStatus = changeTicketInfo['result']['ticketStatus']
                if ticketStatus== 6:#占座成功调确认改签接口
                    dicTieketInfo['accPayAmount'] = float(changeTicketInfo['result']['changeGapFee']) + float(
                        changeTicketInfo['result']['changeFee'])
                    self.train_ticket_confirmChangeTicket(dicTieketInfo)
                    return dicTieketInfo
                elif ticketStatus == 4:
                    while True:#这个循环是为了占座失败立马返回的
                        caseParamData['orderType'] = '1'
                        dicTieketInfo = self.order_pay(caseParamData)
                        dicTieketInfo['orderType'] = '2'  # dicOrderInfo['orderType']: 1:下单。2：改签
                        dicTieketInfo['changeType'] = caseParamData['changeType']
                        ticketInfo = self.train_query_findTrainByStation(dicTieketInfo)
                        for values in ticketInfo:
                            if caseparam.__contains__(values):
                                caseparam[values] = ticketInfo[values]
                        req_json = self.http_request.http_req_type(caseparam, interfaceName, '0')
                        if req_json['errCode'] == '10000':
                            continue
    def train_ticket_confirmChangeTicket(self,dicTicketInfo):#确认改签接口
        #dicTicketInfo['ticket_id']
        #dicTicketInfo['ticketPrice']
        #dicTicketInfo['orderCode']
        interfaceName = 'train/ticket/confirmChangeTicket'
        fname = ("../data/TestData_shijf.xls")
        sheetName = ("train_ticket_confirmChangeTicke")
        caseParam=self.baseConfig.getParamByCaseID(fname,sheetName,'1')
        caseParam['appType'] = fengmao_Global.get_value('appType')
        if float(dicTicketInfo['accPayAmount'])>0:
            caseParam['accPayAmount'] = dicTicketInfo['accPayAmount']
        else:
            caseParam['accPayAmount'] = '0'
        caseParam['ticketId'] = dicTicketInfo['ticket_id']
        caseParam['payPwd'] = fengmao_Global.get_value('pay_password')
        self.http_request.http_req_type(caseParam,interfaceName,'0')
    def train_contact_findList(self):#火车票常用联系人查询接口
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        internfaceName = 'train/contact/findList'
        Contact_param={'submitTime': '20160714090000','appVersion': '2.1.3','appType':fengmao_Global.get_value('appType'),'osname': 'IOS','mobile':fengmao_Global.get_value('mobile')}
        req_json = self.http_request.http_req_type(Contact_param, internfaceName, '0')
        return req_json['result']
    def train_contact_addOrUpdate(self):#添加常用联系人接口
        #self.newUserLogin({'mobile':'15757185534','appType':'M'})
        internfaceName = 'train/contact/addOrUpdate'
        fname = ("../data/TestData_shijf.xls")
        sheetName = ("train_contact_addOrUpdate")
        caseAmount = self.baseConfig.openExcel(fname,sheetName).nrows
        #print (caseAmount)
        for i in range(1,caseAmount):
            caseParam = self.baseConfig.getParamByCaseID(fname, sheetName, str(i))
            caseParam['appType'] = fengmao_Global.get_value('appType')
            req_json = self.http_request.http_req_type(caseParam,internfaceName,'0')
            if req_json['errCode'] == '10000':
                if caseParam['passengerType'] == '1':
                    if "-" not in caseParam['birthday']:
                        caseParam['birthday'] = time.strftime("%Y-%m-%d",time.strptime(caseParam['birthday'],"%Y%m%d"))
                        # print(caseParam['birthday'])
                    mysql = DB()
                    #print(fengmao_Global.get_value('user_id'))
                    checkSql = "SELECT * FROM train_contact " \
                               "WHERE PASSENGER_TYPE = "+caseParam['passengerType']+" AND PASSENGER_NAME = "+"'"+caseParam['passengerName']+"'"+" " \
                               "AND ID_TYPE = "+"'"+caseParam['idType']+"'"+" AND ID_CARD = "+"'"+caseParam['idCard']+"'"+" " \
                               "AND VALID_STATUS = 1 AND SEX ="+"'"+caseParam['sex']+"'"+" AND BIRTHDAY = "+"'"+caseParam['birthday']+"'"+"AND USER_ID = "+"'"+str(fengmao_Global.get_value('user_id'))+"'"+"; "
                    print(checkSql)
                    if len(mysql.dbselect(checkSql)) == 1:
                        self.baseConfig.whriteExcel(fname,sheetName,str(i),'result','pass')
                elif caseParam['passengerType'] == '2':
                    mysql = DB()
                    # print(fengmao_Global.get_value('user_id'))
                    checkSql = "SELECT * FROM train_contact " \
                               "WHERE PASSENGER_TYPE = " + caseParam['passengerType'] + " AND PASSENGER_NAME = " + "'" + \
                               caseParam['passengerName'] + "'" + " " \
                                                                  "AND ID_TYPE = " + "'" + caseParam[
                                   'idType'] + "'" + " AND ID_CARD = " + "'" + caseParam['idCard'] + "'" + " " \
                                                                                                           "AND VALID_STATUS = 1 AND SEX =" + "'" + \
                               caseParam['sex'] + "'" + " AND BIRTHDAY = " + "'" + caseParam[
                                   'birthday'] + "'" + "AND USER_ID = " + "'" + str(
                        fengmao_Global.get_value('user_id')) + "'" + "; "
                    print(checkSql)
                    if len(mysql.dbselect(checkSql)) == 1:
                        cellsite = str('Y'+str(i))
                        self.baseConfig.whriteXLWexcel(fname,sheetname,cellsite,'pass')
                else:
                    cellsite = str('Y' + str(i))
                    self.baseConfig.whriteXLWexcel(fname, sheetname, cellsite, 'pass')
            else:
                cellsite = str('Y' + str(i))
                self.baseConfig.whriteXLWexcel(fname, sheetname, cellsite, 'fail')
    def train_ticket_cancelChangeTicket(self,ticketID):#取消改签接口
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        internfaceName = 'train/ticket/cancelChangeTicket'
        caseParam={'submitTime': '20160714090000','appVersion': '2.1.3',
                   'appType':fengmao_Global.get_value('appType'),
                   'osname': 'IOS'}
        caseParam['ticketId'] = ticketID
        caseParam['appType'] = fengmao_Global.get_value('appType')
        req_json = self.http_request.http_req_type(caseParam,internfaceName,'0')
        if req_json['errCode'] == '10000':
            logger.info('取消改签申请成功')
        else:
            logger.error('取消改签接口申请失败,车票ID：%s',ticketID)
    def train_ticket_cancelOrder(self,orderCode):#取消火车票订单
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        internfaceName = 'train/ticket/cancelOrder'
        caseParam={'submitTime': '20160714090000','appVersion': '2.1.3',
                   'appType':fengmao_Global.get_value('appType'),
                   'osname': 'IOS'}
        caseParam['orderCode'] = orderCode
        req_json = self.http_request.http_req_type(caseParam,internfaceName,'0')
        if req_json['errCode'] == '10000':
            logger.info('取消火车票订单成功')
        else:
            logger.error('取消火车票订单失败,订单编码：%s',orderCode)
    def train_ticket_getChangeTicketInfo(self,ticket_Id):#查询改签信息
        interfaceName = 'train/ticket/getChangeTicketInfo'
        fname = ("../data/TestData_shijf.xls")
        sheetName = ("train_ticket_getChangeTicketInf")
        caseParam = self.baseConfig.getParamByCaseID(fname, sheetName, '1')
        caseParam['appType'] = fengmao_Global.get_value('appType')
        caseParam['ticketId'] = ticket_Id
        return self.http_request.http_req_type(caseParam,interfaceName,'0')
    def train_ticket_insure_refund(self,passengerId):#申请退保接口
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        internfaceName = 'train/ticket/insure/refund'
        caseParam={'submitTime': '20160714090000','appVersion': '2.1.3',
                   'appType':fengmao_Global.get_value('appType'),
                   'osname': 'IOS'}
        caseParam['passengerId'] = passengerId
        req_json = self.http_request.http_req_type(caseParam,internfaceName,'0')
        if req_json['errCode'] == '10000':
            logger.info('申请退保接口请求成功')
        else:
            logger.error('申请退保接口请求失败%s',passengerId)
    def train_query_findTrainByStation(self,dicOrderInfo):#站站查询
        #self.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
        # dicOrderInfo['orderType']: 1:下单。2：改签
        # dicOrderInfo['changeType']: 1:低改高。2：平价改。3高改低
        # dicOrderInfo['ticketPrice']:原车票价格
        # dicOrderInfo['seatClass'] :座位类型类型
        #self.newUserLogin({'mobile':'15757185534','appType':'M'})
        #火车票站站查询接口
        internfaceName = 'train/query/findTrainByStation'
        fname = ("../data/TestData_shijf.xls")
        sheetName = ("train_query_findTrainByStation")
        dicSeat={}
        while 1:
            datNum = random.randint(20, 30)
            delta = datetime.timedelta(days=datNum)
            now = datetime.datetime.now()
            trainDate = now+delta
            caseParam = self.baseConfig.getParamByCaseID(fname,sheetName,'1')
            caseParam['appType'] = fengmao_Global.get_value('appType')
            caseParam['submitTime'] = time.strftime("%Y%m%d%H%M%S")
            caseParam['trainDate'] =trainDate.strftime("%Y-%m-%d")
            req_json= self.http_request.http_req_type(caseParam,internfaceName,'0')
            #根据接口返回获取需要的座位数据
            if len(req_json['result']['trains'])>0:
                if dicOrderInfo['orderType'] == '1':
                    #print len(req_json['result']['trains'])
                    trainsNum = random.randint(0, int(len(req_json['result']['trains']))-1)
                    trains = req_json['result']['trains'][trainsNum]
                    for tickets in trains['tickets']:
                        if float(tickets['seats']) > 0 and (tickets['seatClass'] == dicOrderInfo['seatClass']):
                            dicSeat['trainNo']= trains['trainNo']
                            dicSeat['fromStation'] = trains['fromStation']
                            dicSeat['trainDate'] = req_json['result']['trainDate']
                            dicSeat['queryKey'] = req_json['result']['queryKey']
                            dicSeat['trainClass'] =trains['trainClass']
                            dicSeat['toStation'] = trains['toStation']
                            dicSeat['seatClass'] = tickets['seatClass']
                            dicSeat['buyFee'] = tickets['buyFee']
                            dicSeat['price'] = tickets['price']
                            dicSeat['seatName'] = tickets['seatName']
                            #print (dicSeat)
                            return dicSeat
                elif dicOrderInfo['orderType'] == '2':
                    if dicOrderInfo['changeType'] == '1':# dicOrderInfo['changeType']: 1:低改高。2：平价改。3高改低
                        for trains in req_json['result']['trains']:
                            #print trains
                            for tickets in trains['tickets']:
                                if float(tickets['seats']) > 0 and (float(tickets['price']) > float(dicOrderInfo['ticketPrice'])):
                                    dicSeat['trainNo'] = trains['trainNo']
                                    dicSeat['startStation'] = trains['fromStationCode']
                                    dicSeat['fromStation'] = trains['fromStation']
                                    dicSeat['toStation'] = trains['toStation']
                                    dicSeat['trainDate'] = ("%s-%s-%s"%(req_json['result']['trainDate'][0:4],req_json['result']['trainDate'][4:6],req_json['result']['trainDate'][6:8]))
                                    dicSeat['arrivalDate'] = ("%s-%s-%s"%(req_json['result']['trainDate'][0:4],req_json['result']['trainDate'][4:6],req_json['result']['trainDate'][6:8]))
                                    dicSeat['queryKey'] = req_json['result']['queryKey']
                                    dicSeat['endStation'] = trains['toStationCode']
                                    dicSeat['seatClass'] = tickets['seatClass']
                                    dicSeat['buyFee'] = tickets['buyFee']
                                    dicSeat['price'] = tickets['price']
                                    dicSeat['seatName'] = tickets['seatName']
                                    dicSeat['trainType'] = trains['trainClass']
                                    dicSeat['orderCode'] = dicOrderInfo['orderCode']
                                    dicSeat['ticketId'] = dicOrderInfo['ticket_id']
                                    #print(dicSeat)
                                    return dicSeat
                    elif dicOrderInfo['changeType'] == '2':# dicOrderInfo['changeType']: 1:低改高。2：平价改。3高改低
                        for trains in req_json['result']['trains']:
                            #print trains
                            for tickets in trains['tickets']:
                                if float(tickets['seats']) > 0 and float(tickets['price']) == float(dicOrderInfo['ticketPrice']):
                                    dicSeat['trainNo'] = trains['trainNo']
                                    dicSeat['startStation'] = trains['fromStationCode']
                                    dicSeat['fromStation'] = trains['fromStation']
                                    dicSeat['toStation'] = trains['toStation']
                                    dicSeat['trainDate'] = ("%s-%s-%s" % (
                                    req_json['result']['trainDate'][0:4], req_json['result']['trainDate'][4:6],
                                    req_json['result']['trainDate'][6:8]))
                                    dicSeat['arrivalDate'] = ("%s-%s-%s" % (
                                    req_json['result']['trainDate'][0:4], req_json['result']['trainDate'][4:6],
                                    req_json['result']['trainDate'][6:8]))
                                    dicSeat['queryKey'] = req_json['result']['queryKey']
                                    dicSeat['endStation'] = trains['toStationCode']
                                    dicSeat['seatClass'] = tickets['seatClass']
                                    dicSeat['buyFee'] = tickets['buyFee']
                                    dicSeat['price'] = tickets['price']
                                    dicSeat['seatName'] = tickets['seatName']
                                    dicSeat['trainType'] = trains['trainClass']
                                    dicSeat['orderCode'] = dicOrderInfo['orderCode']
                                    dicSeat['ticketId'] = dicOrderInfo['ticket_id']
                                    #print(dicSeat)
                                    return dicSeat
                    elif dicOrderInfo['changeType'] == '3':# dicOrderInfo['changeType']: 1:低改高。2：平价改。3高改低
                        for trains in req_json['result']['trains']:
                            #print trains
                            for tickets in trains['tickets']:
                                if float(tickets['seats']) > 0 and float(tickets['price']) < float(dicOrderInfo['ticketPrice']):
                                    dicSeat['trainNo'] = trains['trainNo']
                                    dicSeat['startStation'] = trains['fromStationCode']
                                    dicSeat['fromStation'] = trains['fromStation']
                                    dicSeat['toStation'] = trains['toStation']
                                    dicSeat['trainDate'] = ("%s-%s-%s" % (
                                    req_json['result']['trainDate'][0:4], req_json['result']['trainDate'][4:6],
                                    req_json['result']['trainDate'][6:8]))
                                    dicSeat['arrivalDate'] = ("%s-%s-%s" % (
                                    req_json['result']['trainDate'][0:4], req_json['result']['trainDate'][4:6],
                                    req_json['result']['trainDate'][6:8]))
                                    dicSeat['queryKey'] = req_json['result']['queryKey']
                                    dicSeat['endStation'] = trains['toStationCode']
                                    dicSeat['seatClass'] = tickets['seatClass']
                                    dicSeat['buyFee'] = tickets['buyFee']
                                    dicSeat['price'] = tickets['price']
                                    dicSeat['seatName'] = tickets['seatName']
                                    dicSeat['trainType'] = trains['trainClass']
                                    dicSeat['orderCode'] = dicOrderInfo['orderCode']
                                    dicSeat['ticketId'] = dicOrderInfo['ticket_id']
                                    #print(dicSeat)
                                    return dicSeat
    def user_couponList(self):#获取用户优惠券
        internfaceName = 'user/couponList'
        fname = ("../data/TestData_shijf.xls")
        sheetName = ("user_couponList")
        caseParam = self.baseConfig.getParamByCaseID(fname,sheetName,'1')
        return self.http_request.http_req_type(caseParam,internfaceName,'0')
    def insert_ECcoupon(self,userid,couponPrice,userType):
        inserSQL = ("INSERT INTO `ec_coupon_user` "
                    "(`USER_ID`, `SCENE_ID`, `SCENE_CODE`, `COUPON_ID`, `COUPON_NAME`, `DISCOUNT_AMOUNT`, `USE_START_AMOUNT`, `IS_MAY_DAMAGE`, `COUPON_TYPE_CODE`, `USER_TYPE`, `RECEIVE_TIME`, `BEGIN_TIME`, `EXPIRE_TIME`, `USE_TIME`, `EXPAND_CONFIG`, `RECEIVE_NUM`, `STATUS`, `BUSI_CODE`, `RECEIVE_BATCH`, `IS_REMIND`) "
                    "VALUES "
                    "("+"'"+str(userid)+"'"+", '26', 'act_buy_train_1', '36', '一元抢购', "+"'"+str(couponPrice)+"'"+", '0', '2', 'DEDUC_COUPON', "+"'"+str(userType)+"'"+", '2017-08-03 15:56:26', '2017-08-03 15:56:26', '2018-09-02 15:56:26', NULL, NULL, '1', '1', NULL, NULL, '1');")
        self.Mysql_db.dbInsert(inserSQL)
        selectSQL = "SELECT REC_ID FROM ec_coupon_user WHERE USER_ID = " + str(
            userid) + " AND USE_TIME IS NULL AND STATUS = 1 AND COUPON_ID = 36 AND DISCOUNT_AMOUNT = "+str(couponPrice)
        return self.Mysql_db.dbselect(selectSQL)[0]['REC_ID']
    def newUserLogin(self,APIdicparam):
      #这个方法传进来mobile和apptype即可，密码默认111111。apptype传C，M，A不要传数字
      logging.config.fileConfig("../data/logger.conf")
      logger = logging.getLogger("example01")
      baseUrl = self.baseConfig.openTxtFile("../data/baseConfig.txt")
      userLoginInterface = "d-app/API/newUserLogin?"
      #读取参数
      appType = APIdicparam['appType']   #注册用户类型
      mobile = APIdicparam['mobile']  #注册手机号
      key = '3f3fe1b3f38ffd5e01d16bb8839c2214'
      submitTime = APIdicparam['submitTime']
      passWord = '111111'
      sign = oldMd5sign(key+submitTime+mobile)
      #登录接口
      userLoginUrl = baseUrl+userLoginInterface+\
                     'submitTime='+submitTime+'&sign='+sign+'&appVersion=appVersion&appType='\
                     +appType+'&osname=ANDROID&mobile='+mobile+'&passWord='+passWord
      logger.info(userLoginUrl)
      r = requests.get(userLoginUrl)
      if r.status_code == 200:
          result = r.json()
          logger.info(r.text)
          if result['success'] == True:
            #print r.text
            logger.info('登录成功')
            fengmao_Global.set_value('appSessionID', result['result'][0]['sessionId'])
            fengmao_Global.set_value('secret', result['result'][0]['secret'])
            fengmao_Global.set_value('mobile', mobile)
            fengmao_Global.set_value('appType',APIdicparam['appType'])
            My_sql = DB()
            if APIdicparam['appType'] == 'M':
                payPwd=My_sql.dbselect(
                    "SELECT PAY_PASSWORD FROM mem_user WHERE LOGIN_ACCOUNT =" +"'"+mobile +"'"+ " AND SUB_USER_TYPE ='2' ")[0]['PAY_PASSWORD']
                userID = My_sql.dbselect(
                    "SELECT USER_ID FROM mem_user WHERE LOGIN_ACCOUNT =" + "'" + mobile + "'" + " AND SUB_USER_TYPE ='2' ")[
                    0]['USER_ID']
                fengmao_Global.set_value('user_id',userID)
                fengmao_Global.set_value('user_type','2')
                fengmao_Global.set_value('pay_password', payPwd)
            elif APIdicparam['appType'] == 'C':
                payPwd =My_sql.dbselect(
                    "SELECT PAY_PASSWORD FROM mem_user WHERE LOGIN_ACCOUNT =" +"'"+mobile +"'"+ " AND SUB_USER_TYPE ='4'")[0]['PAY_PASSWORD']
                userID = My_sql.dbselect(
                    "SELECT USER_ID FROM mem_user WHERE LOGIN_ACCOUNT =" + "'" + mobile + "'" + " AND SUB_USER_TYPE ='4' ")[
                    0]['USER_ID']
                fengmao_Global.set_value('user_id', userID)
                fengmao_Global.set_value('user_type', '4')
                fengmao_Global.set_value('pay_password', payPwd)
            else:
                payPwd =My_sql.dbselect(
                    "SELECT PAY_PASSWORD FROM mem_user WHERE LOGIN_ACCOUNT =" +"'"+mobile +"'"+ " AND SUB_USER_TYPE ='3' ")[0]['PAY_PASSWORD']
                userID = My_sql.dbselect(
                    "SELECT USER_ID FROM mem_user WHERE LOGIN_ACCOUNT =" + "'" + mobile + "'" + " AND SUB_USER_TYPE ='3' ")[
                    0]['USER_ID']
                fengmao_Global.set_value('user_id', userID)
                fengmao_Global.set_value('user_type', '3')
                fengmao_Global.set_value('pay_password', payPwd)
            return result
          else:
            #print r.text
            logger.info('登录失败')
      else:
            logger.error('接口不通')
            exit()
    def userRegister(self,dicRegister):
        baseUrl = "http://test.eyuntx.com/"
        userRegisterInterface = "d-app/API/userRegister?"
        # 读取参数
        appType = dicRegister['appType']  # 注册用户类型
        mobile  = dicRegister['mobile']  # 注册手机号
        passwd  = dicRegister['passWord']  # 密码
        verCodeType = dicRegister['verCodeType']  # 验证码	0：无类型（兼容老版），1：注册，2：找回登陆密码，3：支付密码设置，4：解绑微信，5：提现，6：解绑银行卡
        if appType == 'M':
            subusertype = '2'
        elif appType == 'C':
            subusertype = '4'
        else:
            subusertype = '3'
        db_MYSQL = DB()
        sql = 'delete from mem_user where LOGIN_ACCOUNT = ' + '"' + mobile + '"' + 'and SUB_USER_TYPE=' + subusertype
        #sql = 'update mem_user set LOGIN_ACCOUNT = ' + '"'+mobile+ '**"' + ' where LOGIN_ACCOUNT = '+'"'+mobile+'"' ' and SUB_USER_TYPE = ' + subusertype   #讲道理sql没错的啊 就是用不了
        db_MYSQL.dbDelete(sql)
        key = '3f3fe1b3f38ffd5e01d16bb8839c2214'
        submitTime = '20160714090000'
        sign = oldMd5sign(key + submitTime + mobile)
        getAuthCode = general_getAuthCode()
        AuthCode = getAuthCode.general_getAuthCode(mobile, appType, verCodeType)
        userRegisterUrl = baseUrl + userRegisterInterface + 'submitTime=20160714090000&sign=' + sign + '&appVersion=appVersion&appType=' + appType + '&osname=ANDROID&mobile=' + str(
            mobile) + '&passWord=' + str(passwd) + '&verifyCode=' + str(AuthCode)
        logger.info(userRegisterUrl)
        registerRequest = requests.get(userRegisterUrl)
        result = registerRequest.json()
        logger.info(registerRequest.text)
        # 判断接口是否请求成功
        if result['success'] == True:
            logger.info('注册成功')
            fengmao_Global.set_value('appSessionID',result['result']['sessionId'])
            fengmao_Global.set_value('secret', result['result']['secret'])
            fengmao_Global.set_value('mobile',mobile)
            return result
        else:
            logger.info("注册失败")
    def merchant_setMerchantBasicAgent(self,APIdicParam):
        baseConfig = openExcel()
        baseUrl = baseConfig.openTxtFile("../data/baseConfig.txt")
        # 定义接口参数
        merchant_setMerchantBasicAgentInterface = "d-app/API/merchant/setMerchantBasicAgent?"
        loginResult = fengmaoAPI_method()
        if loginResult is not None:
            baseConfig = openExcel()
            # 获取sessionID和secret
            appSessionID = fengmao_Global.get_value('appSessionID')
            secret = fengmao_Global.get_value('secret')
            # 签名需要的参数
            dicparam = {'submitTime': APIdicParam['submitTime'],
                        'appVersion': APIdicParam['appVersion'],
                        'appType': APIdicParam['appType'],
                        'osname': APIdicParam['osname'],
                        'identNo': APIdicParam['identNo'],
                        'mobile': '15757185534',
                        'realName': APIdicParam['realName']
                        }
            sign = md5encryption(dicparam, secret)
            # 请求url
            httpResult = httpRequest()
            r = httpResult.HttpGetRequest(baseUrl, merchant_setMerchantBasicAgentInterface, dicparam, appSessionID,
                                          sign)
            result = r.json()
            logger.info(r.text)
            if result['success'] == True:
                logger.info('接口请求成功')
            else:
                logger.info('接口请求失败')
    def user_payPw_update(self,APIdicParam):
        baseConfig = openExcel()
        baseUrl = baseConfig.openTxtFile("../data/baseConfig.txt")
        # 定义接口参数
        merchant_setMerchantBasicAgentInterface = "d-app/API/user/payPw/update?"
        baseConfig = openExcel()
        # 获取sessionID和secret
        appSessionID = fengmao_Global.get_value('appSessionID')
        secret = fengmao_Global.get_value('secret')
        # 获取设置支付密码需要的验证码
        AuthCode = general_getAuthCode()
        verifyCode = AuthCode.general_getAuthCode(APIdicParam['mobile'],APIdicParam['appType'],'3')
        # 签名需要的参数
        dicparam = {'submitTime': APIdicParam['submitTime'],
                    'appVersion': APIdicParam['appVersion'],
                    'appType': APIdicParam['appType'],
                    'osname': APIdicParam['osname'],
                    #确认新密码
                    'confirmNewPwd':APIdicParam['confirmNewPwd'],
                    #登录密码，首次设置时要传入登陆密码
                    'loginPwd':APIdicParam['loginPwd'],
                    #手机号
                    'mobile':APIdicParam['mobile'],
                    #新密码
                    'nowPwd':APIdicParam['nowPwd'],
                    #	验证码
                    'verifyCode':verifyCode
                    }
        sign = md5encryption(dicparam, secret)
        # 请求url
        httpResult = httpRequest()
        r = httpResult.HttpGetRequest(baseUrl, merchant_setMerchantBasicAgentInterface, dicparam, appSessionID,
                                      sign)
        result = r.json()
        logger.info(r.text)
        if result['success'] == True:
            logger.info('设置支付密码接口请求成功')
        else:
            logger.info('设置支付密码接口请求失败')
    def current_give_amount(self,ORIG_PRICE,cycleCount):
        surplusAmount = ORIG_PRICE % cycleCount;
        everyAmount = (ORIG_PRICE - surplusAmount) / cycleCount;
        firstGiveAmount = everyAmount + surplusAmount;
        return firstGiveAmount
    def initData(self,appType,mobile):
        dic = {'submitTime': '20160714090000',
                        'appVersion': '2.1.3',
                        'appType': ''+appType+'',
                        'osname': 'IOS',
                        'identNo': '330184199305203512',
                        'mobile': ''+mobile+'',
                        'realName': '施继峰',
                        'passWord':'111111',
                        'verCodeType':'1'}
        self.userRegister(dic)
        self.merchant_setMerchantBasicAgent(dic)
        self.user_payPw_update({'submitTime': '20160714090000',
                        'appVersion': '2.1.3',
                        'appType': ''+appType+'',
                        'osname': 'IOS',
                    #确认新密码
                    'confirmNewPwd':'111111',
                    #登录密码，首次设置时要传入登陆密码
                    'loginPwd':'111111',
                    #手机号
                    'mobile':'15700000000',
                    #新密码
                    'nowPwd':'111111'})
        if fengmao_Global.get_value('appSessionID') is not None:
            return '数据初始化成功'

    # def merchant_getDiscountByUserId(self):
    #     baseConfig = openExcel()
    #     baseUrl = baseConfig.openTxtFile("../data/baseConfig.txt")
    #     # 定义接口参数
    #     merchant_setMerchantBasicAgentInterface = "d-app/API/user/payPw/update?"
    #     baseConfig = openExcel()
    #     # 获取sessionID和secret
    #     appSessionID = fengmao_Global.get_value('appSessionID')
    #     secret = fengmao_Global.get_value('secret')
    #     # 获取设置支付密码需要的验证码
    #     AuthCode = general_getAuthCode()
    #     verifyCode = AuthCode.general_getAuthCode(APIdicParam['mobile'], APIdicParam['appType'], '3')
    #     # 签名需要的参数
    #     dicparam = {'submitTime': '20160714090000',
    #                 'appVersion': '2.1.3',
    #                 'appType': 'M',
    #                 'osname': 'IOS',
    #                 }
    #     sign = md5encryption(dicparam, secret)
    #     # 请求url
    #     httpResult = httpRequest()
    #     r = httpResult.HttpGetRequest(baseUrl, merchant_setMerchantBasicAgentInterface, dicparam, appSessionID,
    #                                   sign)
    #     result = r.json()
    #     logger.info(r.text)
    #     if result['success'] == True:
    #         logger.info('设置支付密码接口请求成功')
    #     else:
    #         logger.info('设置支付密码接口请求失败')
    def initUserData(self,appType,login_Account):
        user_insertSQL = "INSERT INTO `mem_user` (`LOGIN_ACCOUNT`, `BIND_MOBILE`, `EMAIL`, `PASSWORD`, `REG_TYPE`, `USER_TYPE`, `SUB_USER_TYPE`, `PARENT_ID`, `PARENT_STATUS`, `USER_LEVEL`, `PWD_SECURITY_LEVEL`, `LOGIN_SOURCE`, `DEPUTY_LOGIN_ACCOUNT`, `OPEN_ID`, `PORTRAIT_IMG_URL`, `NICK_NAME`, `REAL_STATUS`, `REAL_NAME`, `REG_TIME`, `RECOMMEND_CODE`, `PAY_PASSWORD`, `CITY_CODE`, `COUNTY_CODE`, `STATUS`, `REG_SOURCE`) " \
                   "VALUES ('"+login_Account+"', '"+login_Account+"', NULL, '96e79218965eb72c92a549dd5a330112', '2', '1', "+appType+", '200002', '3', NULL, '0', NULL, NULL, NULL, NULL, '胜天半子', '3', '胜天一子', '2016-11-01 01:29:44', '30d41', 'c78b6663d47cfbdb4d65ea51c104044e', NULL, NULL, '1', NULL);"
        db = DB()
        db.dbInsert(user_insertSQL)
        userID = db.dbselect("SELECT USER_ID FROM mem_user WHERE SUB_USER_TYPE = "+appType+" AND LOGIN_ACCOUNT = "+login_Account)[0]['USER_ID']
        #print userID
        user_INCOME_BOOK_insertSQL ="INSERT INTO `bm_user_book` ( `USER_ID`, `BOOK_CODE`, `BOOK_BALANCE`, `CREATE_TIME`) VALUES ("+"'"+str(userID)+"'"+", 'INCOME_BOOK', '4000', '2016-11-29 02:30:37');"
        user_PRE_AWARD_BOOK_insertSQL ="INSERT INTO `bm_user_book` ( `USER_ID`, `BOOK_CODE`, `BOOK_BALANCE`, `CREATE_TIME`) VALUES ( "+"'"+str(userID)+"'"+", 'PRE_AWARD_BOOK', '6', '2016-11-06 09:22:18');"
        user_PRE_BOOK_insertSQL ="INSERT INTO `bm_user_book` ( `USER_ID`, `BOOK_CODE`, `BOOK_BALANCE`, `CREATE_TIME`) VALUES ( "+"'"+str(userID)+"'"+", 'PRE_BOOK', '182', '2016-11-01 09:52:29');"
        user_PRE_LINE_BOOK_insertSQL ="INSERT INTO `bm_user_book` ( `USER_ID`, `BOOK_CODE`, `BOOK_BALANCE`, `CREATE_TIME`) VALUES ( "+"'"+str(userID)+"'"+", 'PRE_LINE_BOOK', '12200', '2016-11-06 09:22:18');"
        #print user_INCOME_BOOK_insertSQL
        db.dbInsert(user_INCOME_BOOK_insertSQL)
        db.dbInsert(user_PRE_AWARD_BOOK_insertSQL)
        db.dbInsert(user_PRE_BOOK_insertSQL)
        db.dbInsert(user_PRE_LINE_BOOK_insertSQL)
    def deleteUserData(self,appType,login_Account):
        db = DB()
        db.dbDelete("DELETE FROM mem_user "
                    "WHERE login_account = "+login_Account+" AND SUB_USER_TYPE = "+appType+";")
        #print "DELETE FROM mem_user WHERE login_account = "+login_Account+" AND SUB_USER_TYPE = "+appType+";"

if __name__ == '__main__':

    baseConfig = openExcel()
    http_request = http_req()
    Mysql_db = DB()
    test1 = fengmaoAPI_method()
    # fname = ("../data/TestData_shijf.xls")
    # sheetname = ("train_ticket_case")
    # caseCount = baseConfig.openExcel(fname, sheetname).nrows#获取case个数
    # print(caseCount)
    # # print(time.strptime('19860303', "%Y%m%d"))
    # # print(time.strftime("%Y-%m-%d",time.strptime('19860303', "%Y%m%d")))
    # # test1.newUserLogin({'mobile': '15757185534', 'appType': 'C'})
    # # casaskdas = test1.train_ticket_getChangeTicketInfo('21762')
    # # print(json.dumps(casaskdas))
    # # print(type(casaskdas))
    # test1.insert_ECcoupon('200001',2000,'2')
    # #执行case
    # for i in range(1,caseCount):
    #     caseParamData = baseConfig.getParamByCaseID(fname,sheetname,str(i))
    #     caseParamData['submitTime'] = time.strftime("%Y%m%d%H%M%S")
    #     test1.newUserLogin(caseParamData)
    #     #test1.train_ticket_applyRefundOrder('917816450008')
    #     # test1.train_contact_addOrUpdate()#先添加case需要的乘客
    #     if caseParamData['orderType'] == '1':
    #         test1.order_pay(caseParamData)
    #     else:
    #         test1.train_ticket_applyChangeTicket(caseParamData)


















    #print (test1.train_ticket_applyRefundOrder('9'))
    #test1.newUserLogin({'mobile': '15757185534', 'appType': 'M'})
     #test1.initData()
    # test1.user_payPw_update({'submitTime': '20160714090000',
    #                     'appVersion': '2.1.3',
    #                     'appType': 'M',
    #                     'osname': 'IOS',
    #                 #确认新密码
    #                 'confirmNewPwd':'111111',
    #                 #登录密码，首次设置时要传入登陆密码
    #                 'loginPwd':'111111',
    #                 #手机号
    #                 'mobile':'15700000000',
    #                 #新密码
    #                 'nowPwd':'111111'})
    # test1.newUserLogin({'submitTime': '20160714090000',
    #                     'appVersion': '2.1.3',
    #                     'appType': '',
    #                     'osname': 'IOS',
    #                 #手机号
    #                 'mobile':'15700000000',
    #                 #密码
    #                 'passWord':'111111'})