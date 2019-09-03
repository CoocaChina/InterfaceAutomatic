#?/bin/usr/python
#-*- coding: utf-8 -*-
import os
import paramiko
import threading

class ssh_client():
    def ssh_ifengmao_74(self,cmd):
        ip='139.224.60.74'
        userName = 'userelk'
        passwd = 'userelk'
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, 22, userName, passwd, timeout=5)

            for m in cmd:
                print (m)
                stdin, stdout, stderr = ssh.exec_command(m)
                out = stdout.readlines()
                # 屏幕输出
                for o in out:
                    print(o,)
            print('%s\tOK\n' % (ip))
            ssh.close()
        except:
            print('%s\tError\n' % (ip))


if __name__ == '__main__':
    redis_port = '7979'
    db_name = 'fengmao_db_07_31'
    config_file_name = ['application.properties.man',
                        'application.properties.pro',
                        'application.properties.task',
                        'application.properties.api',
                        'application.properties.partner']
    for filename in config_file_name:
        print (filename)
        # cmd = ["sed -n '/spring\.redis\.port\=/p' /home/userelk/.jenkins/workspace/config/" + filename]  # 你要执行的命令列表
        cmd = [
            "sed -i '/spring\.redis\.port\=7878/s/spring\.redis\.port\=7878/spring\.redis\.port\="+redis_port+"/g' /home/userelk/.jenkins/workspace/config/" + filename,
            "sed -i '/spring\.redis\.port\=7979/s/spring\.redis\.port\=7979/spring\.redis\.port\="+redis_port+"/g' /home/userelk/.jenkins/workspace/config/" + filename,
            "sed -i 's/10\.27\.116\.58\:3306\/.*\?relaxAutoCommit/10\.27\.116\.58\:3306\/"+db_name+"\?relaxAutoCommit/g' /home/userelk/.jenkins/workspace/config/" + filename]
        test1 = ssh_client()
        screen_list = test1.ssh_ifengmao_74(cmd)
        # if screen_list[0] == 'spring.redis.port=7878':
        #     cmd = ["sed -i '/spring\.redis\.port\=7878/s/spring\.redis\.port\=7878/spring\.redis\.port\=7979/g' /home/userelk/.jenkins/workspace/config/" + filename]  # 你要执行的命令列表
        #     test1 = ssh_client()
        #     screen_list = test1.ssh_ifengmao_74(cmd)
        # else:
        #     cmd = ["sed -i '/spring\.redis\.port\=7979/s/spring\.redis\.port\=7979/spring\.redis\.port\=7878/g' /home/userelk/.jenkins/workspace/config/" + filename]  # 你要执行的命令列表
        #     test1 = ssh_client()
        #     screen_list = test1.ssh_ifengmao_74(cmd)
    #获取原来的redis
    #"sed -i '/spring\.redis\.port\=7878/s/spring\.redis\.port\=7878/spring\.redis\.port\=7979/g' application.properties.man"
