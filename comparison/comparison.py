import pymysql.cursors
import logging
import logging.config
import smtplib
from email.mime.text import MIMEText  # 发送文本
from email.utils import formataddr
from email.header import Header
from tools.txt_read import txtCont
    # 获取日志配置文件
# logging.config.fileConfig("../data/logger.conf")
# logger = logging.getLogger("example01")
sender_from = '853467358@qq.com'  # 发件人邮箱
sender_to = 'shijifeng@songxiaocai.com'  # 收件人邮箱
dict = txtCont("../data/baseConfigNew.txt")
print(dict)
host = 'rm-bp129c5236x5x669i2o.mysql.rds.aliyuncs.com'
db = 'sxc'
user = 'sxc_test_server'
password = 'vCMGPP3b9KptEfiY'
class comparison():
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
    #获取所有合同
    def all_contract(self):
        all_contract = self.dbselect("select * from sxc_pc.sxc_store_plan where status in (50)")
        return all_contract
    def ContractComparison(self):
        all_contract = self.all_contract()
        list_error = []
        list_correct = []
        for contract in all_contract:
            #底层库存重量
            warehousing_num = self.up_stock(contract['id'])
            #入库单重量-解除质押-出库单
            wms_num = self.base_stock(contract['id'])
            if int(warehousing_num) == int(wms_num):
                #print('正确')
                list_correct.append(contract)
            else:
                logging.info('对不上了=====合同ID：'+str(contract['id']))
                if int(warehousing_num) - int(wms_num) >0:
                    list_error.append(str(contract['id'])+str('底层库存大于上层库存'))
                #print('错误')
        str1 = "\n".join(map(str,list_error))
        self.send_email('错误合同列表：', str1)
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
    #获取一个合同的底层库存
    def base_stock(self,contract_id):
        #获取合同底层库存集合
        base_stock = self.dbselect("select a.item_id, a.item_name, a.warehouse_id, a.warehouse_hole_id, a.batch_id, a.supplier_id, a.balance, a.create_time, a.modify_time, c.name warehouse_name, d.name warehouse_hole_name, "
            "IFNULL((SELECT SUM(lock_num) FROM sxc_pc.sxc_wms_lock_stock b WHERE b.batch_id=a.batch_id),0) locked "
            "FROM sxc_pc.sxc_wms_stock a "
            "JOIN sxc_pc.sxc_wms_warehouse c ON a.warehouse_id=c.id "
            "JOIN sxc_pc.sxc_wms_warehouse_hole d ON a.warehouse_hole_id=d.id "
            "WHERE a.enable=1 "
            "AND a.batch_id IN "
            "(SELECT batch_id FROM sxc_pc.sxc_warehouse_order_and_batch where state=1 and contract_id = "+str(contract_id)+");")
        #print(base_stock)
        if base_stock == None:
            return 0
        #汇总该合同底层库存
        stock_sum = 0
        for wms_stock in base_stock:
            stock_num = wms_stock['balance']-wms_stock['locked']
            stock_sum = stock_num+stock_sum
        #print('stock====='+str(stock_sum))
        return stock_sum
    #获取一个合同的上层库存
    def up_stock(self,contract_id):
        #获取入库单总重量
        warehousing_stock = self.dbselect('SELECT a.sku_id , a.sku_name , sum(a.`sku_weight`) as sumnum FROM sxc_pc.sxc_warehousing_order_sku a LEFT JOIN sxc_pc.sxc_warehousing_order b on b.id = a.warehousing_order_id '
                    'WHERE a.state = 1 and b.state = 1 and b.status = 60 and b.source_id = '+str(contract_id))

        if warehousing_stock[0]['sumnum'] == None:
            warehousing_stock[0]['sumnum'] = 0
        #获取出库单总重量
        stock_out = self.dbselect('SELECT a.sku_id , a.sku_name , sum(a.`pre_store_weight`/100) as sumnum FROM sxc_pc.pc_stock_out_order_detail a LEFT JOIN sxc_pc.pc_stock_out_order b on b.id = a.stock_out_order_id '
                    'WHERE a.state = 1 and b.state = 1 and b.status = 40 and b.contract_id = '+str(contract_id))

        if stock_out[0]['sumnum'] == None:
            stock_out[0]['sumnum'] = 0
        #获取解除质押担总重量
        relieve_weight = self.dbselect('SELECT a.sku_id , sum(a.`relieve_weight`) as sumnum FROM sxc_pc.pc_relieve_pledge_detail a LEFT JOIN sxc_pc.pc_relieve_pledge b on b.id = a.relieve_pledge_id '
                    'WHERE a.state = 1 and b.state = 1 and b.status = 40 and b.contract_id = '+str(contract_id))

        if relieve_weight[0]['sumnum'] == None:
            relieve_weight[0]['sumnum'] = 0
        #print(warehousing_stock[0]['sumnum'])
        #print(stock_out[0]['sumnum'])
        #print(relieve_weight[0]['sumnum'])
        sum_weight = float(warehousing_stock[0]['sumnum']) - float(stock_out[0]['sumnum']) - float(relieve_weight[0]['sumnum'])
        #print(sum_weight)
        return sum_weight

if __name__ == '__main__':
    comparison_test = comparison();
    comparison_test.ContractComparison()
