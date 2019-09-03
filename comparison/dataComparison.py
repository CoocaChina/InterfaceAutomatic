from tools.mysql_db import DB
from tools.smtp_base import email
import logging
import logging.config

# 获取日志配置文件
logging.config.fileConfig("../data/logger.conf")
logger = logging.getLogger("example01")


class comparison():
    def __init__(self):
        self.selectDB = DB();
        self.sendemail = email();

    # 获取所有合同
    def all_contract(self):
        all_contract = self.selectDB.dbselect("select * from sxc_pc.sxc_store_plan where status in (50)")
        return all_contract

    def ContractComparison(self):
        all_contract = self.all_contract()
        list_error = []
        list_correct = []
        for contract in all_contract:
            # 底层库存重量
            warehousing_num = self.up_stock(contract['id'])
            # 入库单重量-解除质押-出库单
            wms_num = self.base_stock(contract['id'])
            if int(warehousing_num) == int(wms_num):
                # print('正确')
                list_correct.append(contract)
            else:
                logging.info('对不上了=====合同ID：' + str(contract['id']))
                if int(warehousing_num) - int(wms_num) > 0:
                    list_error.append(str(contract['id']) + str('底层库存大于上层库存'))
                # print('错误')
        self.selectDB.close()
        str1 = "\n".join(map(str, list_error))
        self.sendemail.send_email('错误合同列表：', str1)

    # 获取一个合同的底层库存
    def base_stock(self, contract_id):
        # 获取合同底层库存集合
        base_stock = self.selectDB.dbselect(
            "select a.item_id, a.item_name, a.warehouse_id, a.warehouse_hole_id, a.batch_id, a.supplier_id, "
            "a.balance, a.create_time, a.modify_time, c.name warehouse_name, d.name warehouse_hole_name, "
            "IFNULL((SELECT SUM(lock_num) FROM sxc_pc.sxc_wms_lock_stock b WHERE b.batch_id=a.batch_id),0) locked "
            "FROM sxc_pc.sxc_wms_stock a "
            "JOIN sxc_pc.sxc_wms_warehouse c ON a.warehouse_id=c.id "
            "JOIN sxc_pc.sxc_wms_warehouse_hole d ON a.warehouse_hole_id=d.id "
            "WHERE a.enable=1 "
            "AND a.batch_id IN "
            "(SELECT batch_id FROM sxc_pc.sxc_warehouse_order_and_batch where state=1 and contract_id = " + str(
                contract_id) + ");")
        # print(base_stock)
        if base_stock == None:
            return 0
        # 汇总该合同底层库存
        stock_sum = 0
        for wms_stock in base_stock:
            stock_num = wms_stock['balance'] - wms_stock['locked']
            stock_sum = stock_num + stock_sum
        # print('stock====='+str(stock_sum))
        return stock_sum

    # 获取一个合同的上层库存
    def up_stock(self, contract_id):
        # 获取入库单总重量
        warehousing_stock = self.selectDB.dbselect(
            'SELECT a.sku_id , a.sku_name , sum(a.`sku_weight`) as sumnum FROM sxc_pc.sxc_warehousing_order_sku a '
            'LEFT JOIN sxc_pc.sxc_warehousing_order b on b.id = a.warehousing_order_id '
            'WHERE a.state = 1 and b.state = 1 and b.status = 60 and b.source_id = ' + str(contract_id))

        if warehousing_stock[0]['sumnum'] == None:
            warehousing_stock[0]['sumnum'] = 0
        # 获取出库单总重量
        stock_out = self.selectDB.dbselect(
            'SELECT a.sku_id , a.sku_name , sum(a.`pre_store_weight`/100) as sumnum FROM '
            'sxc_pc.pc_stock_out_order_detail a LEFT JOIN sxc_pc.pc_stock_out_order b on b.id = a.stock_out_order_id '
            'WHERE a.state = 1 and b.state = 1 and b.status = 40 and b.contract_id = ' + str(contract_id))

        if stock_out[0]['sumnum'] is None:
            stock_out[0]['sumnum'] = 0
        # 获取解除质押担总重量
        relieve_weight = self.selectDB.dbselect(
            'SELECT a.sku_id , sum(a.`relieve_weight`) as sumnum FROM sxc_pc.pc_relieve_pledge_detail a LEFT JOIN '
            'sxc_pc.pc_relieve_pledge b on b.id = a.relieve_pledge_id '
            'WHERE a.state = 1 and b.state = 1 and b.status = 40 and b.contract_id = ' + str(contract_id))

        if relieve_weight[0]['sumnum'] is None:
            relieve_weight[0]['sumnum'] = 0
        # print(warehousing_stock[0]['sumnum'])
        # print(stock_out[0]['sumnum'])
        # print(relieve_weight[0]['sumnum'])
        sum_weight = float(warehousing_stock[0]['sumnum']) - float(stock_out[0]['sumnum']) - float(
            relieve_weight[0]['sumnum'])
        # print(sum_weight)
        return sum_weight


if __name__ == '__main__':
    comparison_test = comparison();
    comparison_test.ContractComparison()
