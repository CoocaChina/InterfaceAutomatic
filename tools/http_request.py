#?/bin/usr/python
#-*- coding: utf-8 -*-
import json
from base64 import encode
import logging
import requests
import time

import sys

from tools.OpenExcel import openExcel
from tools.fengmao_md5 import md5encryption,oldMd5sign
from tools.fengmao_redis import redisInit
from  tools.txt_read import txtCont
from tools import fengmao_Global

# 获取日志配置文件
logging.config.fileConfig("../data/logger.conf")
logger = logging.getLogger("example01")

class http_req():
    secret=''
    reqURL=''
    def _init_(self,appType):
        dict = txtCont("../data/baseConfigNew.txt")
        self.reqURL = "http://" + dict["apiurl_test"]
    def http_req(self,params_req,method_req):
        self._init_('C')
        interface_Name = method_req
        method=method_req
        params= json.loads(json.dumps(params_req))
        paramString=''
        try:
            del params['result']
        except:
            print ('no result key!')
        try:
            del params['preCode']
        except:
            print ('no preCode key!')
        try:
            del params['sign']
        except:
            print ('no sign key!')
        print (params)
        for key in params:
            sorted(params[key])
        #sign = md5encryption(params, secret)
        sign = oldMd5sign(self.secret+params['submitTime']+params['mobile'])
        for key in params:
            paramString=paramString  + key + '=' + params[key]+ '&'
        #print paramString
        logger.info(self.reqURL + interface_Name + '?' + paramString + 'sign=' + sign)
        r = requests.get(self.reqURL + interface_Name + '?' + paramString + 'sign=' + sign)
        logger.info(r.text)
        return r.json()
        return response
    def http_req_type(self,params_req,method_req,req_type):#req_type=1表示特殊加密方式 =0 表示通用加密方式
        subURL = ''
        return self.http_req_type_full(params_req,method_req,req_type,subURL)

    def http_req_type_full(self, params_req, method_req, req_type,subURL):  # req_type=1表示特殊加密方式 =0 表示通用加密方式
        if req_type == '1':
            return self.http_req(params_req, method_req)
        elif req_type == '0':
            appType = params_req['appType']
            self._init_(appType)
            interface_Name = method_req
            method = method_req
            params = json.loads(json.dumps(params_req))
            paramString = ''
            try:
                del params['result']
                del params['rechargeType']
            except:
                print('no result key!')
            try:
                del params['preCode']
            except:
                print('no preCode key!')
            try:
                del params['sign']
            except:
                print('no sign key!')
            # logger.info(params)
            # for key in params:
            #   sorted(params[key])
            # sign = md5encryption(params, secret)
            # print(fengmao_Global.get_value('secret'))
            sign = md5encryption(params, fengmao_Global.get_value('secret'))
            for key in params:
                paramString = paramString + key + '=' + str(params[key]) + '&'
            # print fengmao_Global.get_value('appSessionID')
            reqURL = self.reqURL + subURL + interface_Name + '?' + paramString + 'sign=' + sign + '&appSessionId=' + fengmao_Global.get_value(
                    'appSessionID')
            logger.info(reqURL)
            r = requests.get(reqURL)
            logger.info(r.text)
            return r.json()

if __name__ == '__main__':
  test = http_req()
  mobile = '13858073331'
  authcode = '1234'
  submitTime= time.strftime("%Y%m%d%H%M%S")
  test1 = openExcel()
  caseParam = test1.getParamByCaseID('../data/TestData_Wujy.xls', 'getAuthCode', 1)
  caseParam['mobile'] = mobile
  caseParam['verCodeType'] = '1'
  caseParam['submitTime'] = submitTime
  #redis1 = redisInit()
  #redis1.redisSetKey('verification_code_1_' + mobile, authcode)
  print (caseParam)
  test = http_req()
  response = test.http_req(caseParam, 'getAuthCode')
  redis1 = redisInit()
  print (redis1.redisGetKey('verification_code_1_' + mobile))
