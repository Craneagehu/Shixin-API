#-*- coding:utf-8 -*-
import json
import os
import shutil
import time
import threading
import pymysql
import requests
import lianzhong_api
from queue import Queue
from bs4 import BeautifulSoup
from fake_useragent import UserAgent




class IndexName(object):

    def __init__(self):
        self.ua = UserAgent()
        self.start_url = 'http://zxgk.court.gov.cn/xgl/'
        self.yzm_url = 'http://zxgk.court.gov.cn/xgl/captchaXgl.do'
        self.check_yzm_url = 'http://zxgk.court.gov.cn/xgl/checkyzm'
        self.post_url = 'http://zxgk.court.gov.cn/xgl/searchXgl.do'
        self.data_list = []
        self.headers = {
            'User-Agent': "PostmanRuntime/7.15.0",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "zxgk.court.gov.cn",
            'cookie': "JSESSIONID=F63BA51751C76CCD1DD5A2FE01FF1C40",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
        }
        self.q = Queue()
        self.lock = threading.Lock()
        self.conn = pymysql.connect(host='localhost',user = 'root',password = 'admin',database='data_query',port = 3306,charset='utf8')
        self.cur = self.conn.cursor()

     #获取验证码id
    def get_captchaid(self):
        headers = {
            'User-Agent': self.ua.random,
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "zxgk.court.gov.cn",
            'cookie': "JSESSIONID=0F26336969AE2E43E4AF769A1DA8EB45",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        response = requests.request("GET", self.start_url, headers=headers)
        response.encoding = 'utf-8'
        html = response.text
        #print(html)
        if html:
            soup = BeautifulSoup(html, 'lxml')
            captchaid = soup.find('img', attrs={'id': 'captchaImg'})['src'].split('?')[1].split('&')[0].split('=')[1]
            #print(captchaid)
        return captchaid

    #得到验证码图片
    def get_captcha(self,captchaid):
        querystring = {"captchaId": captchaid, "random": "0.9207474150007781"}
        response = requests.request("GET",self.yzm_url, headers=self.headers, params=querystring)
        captcha_name = f'_{int(time.time())}'
        with open(f'../spiders/verify_code/{captcha_name}.jpg','wb') as f:
                f.write(response.content)

        return captcha_name
    #识别验证码返回结果
    def get_code(self,captcha_name):
        code = lianzhong_api.main(

            'a1366769',
            '1008611XJ...',
            f'../spiders/verify_code/{captcha_name}.jpg',
            "http://v1-http-api.jsdama.com/api.php?mod=php&act=upload",
            '4',
            '8',
        )
        # 返回验证码
        return code

    #检验验证码是否正确
    def check_yzm(self,captchaid,code):
        querystring = {"captchaId": captchaid, "pCode": code}
        headers = {
            'User-Agent': self.ua.random,
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            #'Postman-Token': "fa755e84-c939-4d09-8b45-527cd425bc45,0cfb1ba6-16d6-4a2d-aecd-70d7f5258e9e",
            'Host': "zxgk.court.gov.cn",
            'cookie': "JSESSIONID=F63BA51751C76CCD1DD5A2FE01FF1C40",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        response = requests.request("GET", self.check_yzm_url, headers=headers, params=querystring)
        response.encoding = 'utf-8'
        return response.text

    #提交表单数据
    def get_page(self,name,cardnum):
        captchaid = self.get_captchaid()
        while True:
            captcha_name = self.get_captcha(captchaid)
            code = self.get_code(captcha_name)
            bool = self.check_yzm(captchaid, code)
            if bool:
                pic = os.listdir('../spiders/verify_code')
                # 将正确识别的验证码复制到独立目录下
                shutil.copyfile(
                    f"../spiders/verify_code/{pic[-1]}",
                    f"../spiders/True/{pic[-1]}")
                break
            else:
                print("验证码识别错误")

        querystring = {
            "captchaId": captchaid,
            'currentPage':1,
            'pCardNum':cardnum,
            'pCode':code,
            'pName':name,
            'searchCourtName':'全国法院（包含地方各级法院）',
            'selectCourtArrange':1,
            'selectCourtId':0

                }

        response = requests.request("POST", self.post_url, headers=self.headers,data=querystring)
        response.encoding = 'utf-8'

        totalsize = json.loads(response.text)[0]["totalSize"]

        if totalsize:
            result = json.loads(response.text)
            pages = result[0]['totalPage']
            return pages, captchaid, code
        else:
            return '未查到相关信息'

    #主函数入口
    def main(self):
        self.lock.acquire()
        try:
            if not self.q.empty():
                group = self.q.get()
                name = group[0]
                cardnum = group[1]
                tup = self.get_page(name,cardnum)

                if tup != '未查到相关信息':
                    for page in range(1, tup[0]+1):
                        querystring = {
                            "captchaId": tup[1],
                            'currentPage': page,
                            'pCardNum': cardnum,
                            'pCode': tup[2],
                            'pName': name,
                            'searchCourtName': '全国法院（包含地方各级法院）',
                            'selectCourtArrange': 1,
                            'selectCourtId': 0

                        }

                        response = requests.request("POST", self.post_url, headers=self.headers, data=querystring)
                        response.encoding = 'utf-8'
                        if response.text:
                            result = json.loads(response.text)

                            data = result[0]['result']
                            for each in data:
                                dic = {}
                                json_data = json.loads(each['jsonObject'],strict=False)

                                #姓名
                                dic['pname'] = json_data['XM'] if 'XM' in json_data else ''

                                #性别
                                dic['sex'] = json_data['ZXFYMC'] if 'ZXFYMC' in json_data else ''

                                #身份证号码
                                dic['cardnum'] = cardnum

                                #立案时间
                                dic['filing_time'] = json_data['LASJ'] if 'LASJ' in json_data  else ''

                                #案号
                                dic['case_num'] = json_data['AH'] if 'AH' in json_data else ''

                                #企业信息
                                dic['enterprise_info'] = json_data['QY_MC'] if 'QY_MC'in json_data else ''

                                self.data_list.append(dic)
                                self.save2Mysql(dic)

                else:
                    self.data_list.append(tup)

                    dic = {}
                    # 姓名
                    dic['pname'] = name

                    # 性别
                    dic['sex'] = ''

                    # 身份证号码
                    dic['cardnum'] = cardnum

                    # 立案时间
                    dic['filing_time'] = ''

                    # 案号
                    dic['case_num'] = ''

                    # 企业信息
                    dic['enterprise_info'] = ''

                    self.save2Mysql(dic)

        except Exception as e:
            print(f"出现异常：{e}")
            self.data_list.append('403')
        self.lock.release()

    #将数据保存到数据库
    def save2Mysql(self,data):
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))

        insert_sql = "insert into xianzhi_xiaofei (%s) values (%s)" % (keys, values)
        self.cur.execute(insert_sql, tuple(data.values()))
        self.conn.commit()

    #开启多线程
    def MyThread(self,name,cardnum):
        self.q.put((name,cardnum))
        threadList = []
        for i in range(6):
            t = threading.Thread(target=self.main)
            threadList.append(t)
            t.start()

        for j in threadList:
            j.join()

        return self.data_list

if __name__ == '__main__':

    t1 = time.time()
    name = '业春'
    cardnum = ''
    index = IndexName()
    index.MyThread(name,cardnum)
    #data = index.main(name,cardnum)
    t2 = time.time()
    print(f"耗时:{t2-t1}s")







