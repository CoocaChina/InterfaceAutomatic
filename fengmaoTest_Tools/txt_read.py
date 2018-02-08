#?/bin/usr/python
#-*- coding: utf-8 -*-
#import sysconfig
def txtCont(txtpath):
    txt_path=txtpath
    rate1 = open(txt_path, 'r')
    dic = dict()
    for line in rate1:
        line = line.strip().split(':')
        dic[line[0]] = line[1].replace(' ','')
    return dic
    rate1.close()

if __name__ == '__main__':
  testdic = txtCont("../data/baseConfigNew.txt")
  print (testdic)
  print (testdic['appkey'])