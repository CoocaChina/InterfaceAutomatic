#?/bin/usr/python
#-*- coding: utf-8 -*-
import requests
import logging
import logging.config
class httpRequest():
  #传入参数baseUrl:测试域名。baseInterface:接口名称（例d-app/API/findTelProductList?）
  #baseparam:接口参数。（例：{appType:M,appVersion:2.1.3}）
  #appSessionID sign
  def HttpGetRequest(self,baseUrl,baseInterface,baseparam,appSessionID,sign):
    # 获取日志配置文件
    logging.config.fileConfig("../data/logger.conf")
    logger = logging.getLogger("HttpGetRequest")
    list1 = list(baseparam.keys())
    list1.sort()
    i = 0
    paramString = ""
    while len(list1) > i:
      paramString = paramString + '&' + list1[i] + '=' + baseparam[list1[i]]
      i += 1
    #print paramString
    r = requests.get(baseUrl+baseInterface+paramString+'&'+'appSessionId='+appSessionID+'&sign='+sign)
    logger.info(baseUrl+baseInterface+paramString+'&'+'appSessionId='+appSessionID+'&sign='+sign)
    #print (baseUrl+baseInterface+paramString+'&'+'appSessionId='+appSessionID+'&sign='+sign)
    return r

