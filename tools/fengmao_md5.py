#?/bin/usr/python
#-*- coding: utf-8 -*-
import hashlib
import os,sys
from imp import reload

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
def md5encryption(dicparam,secret):
  list1 = list(dicparam.keys())
  list1.sort()
  #print (list1)
  i = 0 
  md5String = ""
  while len(list1)>i:
      if i == 0:
        md5String = secret+list1[i]+'='+str(dicparam[list1[i]])
      elif i > 0 and i < len(list1)-1:
        md5String = md5String+'&'+list1[i]+'='+str(dicparam[list1[i]])
        #print (list1[i])
      else:
        md5String = md5String+'&'+list1[i]+'='+str(dicparam[list1[i]])+secret
      i+=1
  #print md5String
  sign = hashlib.md5(md5String.encode(encoding='utf-8'))

  # sign.update(md5String)
  return sign.hexdigest()
def oldMd5sign(md5String):
  sign = hashlib.md5(md5String.encode(encoding='utf-8'))
  # sign.update(md5String)
  return sign.hexdigest()
