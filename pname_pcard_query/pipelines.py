# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql
from twisted.enterprise import adbapi


class PnamePcardQueryPipeline(object):

    def __init__(self):
        self.file = open('F:\Pycharm_projects\Clone2\pname_pcard_query\shixin_flask\query_info.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        item_json = json.dumps(dict(item), ensure_ascii=False)
        #写入文件
        self.file.write(item_json + '\n')
        return item

    def close_spider(self, spider):
        self.file.close()




#异步写入数据
# class MySqlTwistPipeline(object):
#     def __init__(self,dbpool):
#         self.dbpool = dbpool
#
#     @classmethod
#     def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
#         """
#         数据库建立连接
#         :param settings: 配置参数
#         :return: 实例化参数
#         """
#         adbparams = dict(
#             host=settings['MYSQL_HOST'],
#             port=settings["MYSQL_PORT"],
#             db=settings['MYSQL_DBNAME'],
#             user=settings['MYSQL_USER'],
#             password=settings['MYSQL_PASSWORD'],
#             charset="utf8",
#             cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
#         )
#
#         # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
#         dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
#
#         # 返回实例化参数
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#         """
#         使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
#         """
#         query = self.dbpool.runInteraction(self.do_insert,item)  # 指定操作方法和操作数据
#
#         # 添加异常处理
#         query.addCallback(self.handle_error)  # 处理异常
#
#     def do_insert(self,cursor,item):
#         # 对数据库进行插入操作，并不需要commit，twisted会自动commit
#         insert_sql = "insert into xianzhi_xiaofei(pname,sex,filing_time,case_num,enterprise_info) values(%s,%s,%s,%s,%s)"
#         print(insert_sql)
#         print(item)
#         cursor.execute(insert_sql,(item['pname'], item['sex'], item['filing_time'], item['case_num'],item['enterprise_info']))
#
#     def handle_error(self, failure):
#         if failure:
#             # 打印错误信息
#             print(failure)


class MySqlPipeline(object):

    def __init__(self,host,port,user,password,database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            host = crawler.settings.get('MYSQL_HOST'),
            port=crawler.settings.get('MYSQL_PORT'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            database=crawler.settings.get('MYSQL_DBNAME')
        )

    def open_spider(self, spider):
        # 连接数据库
        self.conn = pymysql.connect(self.host,self.user,self.password,self.database,self.port,charset='utf8')
        self.cur = self.conn.cursor()  # 游标

    def process_item(self, item, spider):
        data = dict(item)

        if len(item) == 1:
            pass
        else:
            keys = ','.join(data.keys())
            values = ','.join(['%s'] * len(data))

            insert_sql = "insert into xianzhi_xiaofei (%s) values (%s)" % (keys,values)
            self.cur.execute(insert_sql,tuple(data.values()))
            self.conn.commit()

        return item

    def close_spider(self, spider):
        self.cur.close()  # 关闭游标
        self.conn.close()  # 关闭数据库










