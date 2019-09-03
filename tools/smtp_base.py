import smtplib
from email.mime.text import MIMEText  # 发送文本
from email.mime.image import MIMEImage # 发送图片
from email.mime.multipart import MIMEMultipart # 将多个对象结合起来
from email.utils import formataddr
from email.header import Header

sender_from = '853467358@qq.com' # 发件人邮箱
sender_to='shijifeng@songxiaocai.com' # 收件人邮箱

# 定义一个函数，接收传入的邮件主题，邮件内容为参数
class email():
    def __init__(self):
        print(1)
    def send_email(self,eamil_subject:str,email_content:str)->int:
        try:
             # 构造邮件的内容  plain:表示发送的是文本；HTML：表示发送的超文本
            message = MIMEText(email_content, 'plain', 'utf-8')
             # 主题
            message['Subject'] = Header(eamil_subject, 'utf-8')
            message['From'] = formataddr(['警告大师', sender_from])
            message['To'] = formataddr(['预警大师', sender_to])

            # 构造发送邮件的对象smtp，实例化SMTP()
            smtp = smtplib.SMTP()
            # 连接邮箱服务器 host 和 port
            smtp.connect('smtp.qq.com', 25)   # 可以简写  smtp=smtplib.SMTP('smtp.qq.com',25)
            # 登陆邮箱  第二个参数是qq邮箱授权码
            smtp.login(sender_from, 'hrthyvylnhezbcih')
            # 发送方，接收方（可以有多个['接收地址1'，'接收地址2'，....]），发送的消息（字符串类型，使用邮件格式）
            # message.as_string() 将MIMEText对象变为str
            smtp.sendmail(sender_from, sender_to, message.as_string())
            # 退出邮箱,结束SMTP会话
            smtp.quit()
            return 0
        except:
            return -1

if __name__ == '__main__':
    lsi = [1,2,3]
    sendemail = email()
    email.send_email('111','111')