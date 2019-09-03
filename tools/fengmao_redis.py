#?/bin/usr/python
#-*- coding: utf-8 -*-
import redis
from  tools.txt_read import txtCont
dict = txtCont("../data/baseConfigNew.txt")
host = '120.55.170.91'
port = dict['redis_port']
password = 'Hiwitech@RedisPwd'

class redisInit():
  #初始化redis。连接到测试环境redis
  def __init__(self):
    	self.r = redis.Redis(host = host,port = port,password = password)
  #传入key，获取key对应的值。返回是string
  # def redisGetKey(self,redisKey):
  #     value = (self.r.get(redisKey))
  #     #print ('redisValue is ' + value)
  #     return value
  def redisGetKey(self,redisKey):
      value = (self.r.get(redisKey)).decode('ascii')
      #print ('redisValue is ' + value)
      return value
  #传入key和value，将key的值设置为对应的value，这个没有设置失效时间。需要设置失效时间的key需要重新写方法
  def redisSetKey(self,redisKey,reidsValue):
      return self.r.set(redisKey,reidsValue)
  #删除传入key对应的值
  def redisDeleteKey(self,redisKey):
  	return self.r.delete(redisKey)
  def redisHgetall(self,redisKey):
    return self.r.hgetall(redisKey)
  def redisHget(self,redisKey,reidsKey2):
  	return self.r.hget(redisKey,reidsKey2)
if __name__ == '__main__':
  redis1 = redisInit()
  print (redis1.redisGetKey('BOOK_PRE_BOOK_200001'))
