# -*- coding: utf-8 -*-
import json
import logging
import os
import shutil
import time
import scrapy
from fake_useragent import UserAgent
from pname_pcard_query import lianzhong_api
from urllib.parse import urljoin, urlencode
from pname_pcard_query.items import PnamePcardQueryItem

class NameCardQuerySpider(scrapy.Spider):
    name = 'name_card_query'
    allowed_domains = ['zxgk.court.gov.cn/xgl']
    start_urls = ['http://zxgk.court.gov.cn/xgl/']

    def __init__(self,**kwargs):
        self.pname = kwargs['pname']
        self.pcardnum = kwargs['pcardnum']
        self.index_url = 'http://zxgk.court.gov.cn/xgl/'
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "zxgk.court.gov.cn",
            'cookie': "JSESSIONID=0F26336969AE2E43E4AF769A1DA8EB45",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
        }

    def start_requests(self):

        yield scrapy.Request(self.index_url,headers=self.headers,callback= self.index,dont_filter=True)

    def index(self, response):
        captchaid = response.xpath('//*[@id="captchaImg"]/@src').extract_first()
        captcha_url = urljoin(response.url,captchaid)

        yield scrapy.Request(captcha_url,headers=self.headers,callback=self.get_captchaid,dont_filter=True,meta={'captchaid':captchaid})

    def get_captchaid(self, response):
        #获取验证码二进制文件，并写入图片中
        captcha_name = f'_{int(time.time())}'
        with open(f'F:\\Pycharm_projects\\Clone2\\pname_pcard_query\\spiders\\verify_code\\{captcha_name}.jpg','wb') as f:
            f.write(response.body)
        code = lianzhong_api.main(
                    'a1366769',
                    '1008611XJ...',
                    f'F:\\Pycharm_projects\\Clone2\\pname_pcard_query\\spiders\\verify_code\\{captcha_name}.jpg',
                    "http://v1-http-api.jsdama.com/api.php?mod=php&act=upload",
                    '4',
                    '8',
        )
        captchaid_str = response.meta['captchaid'].split('?')[1].split('&')[0].split('=')[1]
        #print(captchaid_str)
        data = {
            'captchaId':captchaid_str,
            'pCode':code
        }
        params = urlencode(data)
        check_url = 'http://zxgk.court.gov.cn/xgl/checkyzm?' + params

        yield scrapy.Request(check_url,headers=self.headers,callback=self.check_captcha,dont_filter=True,meta=data)

    #检查验证码并提交表单数据
    def check_captcha(self,response):
        try:
            form_url = 'http://zxgk.court.gov.cn/xgl/searchXgl.do'
            check_result = response.body.decode(response.encoding)
            captchaId = response.meta['captchaId']
            pCode = response.meta['pCode']

            #如果返回1表示验证码识别正确，返回0表示未识别成功
            if check_result:
                #列出所有图片名
                pic = os.listdir('F:\\Pycharm_projects\\pname_pcard_query\\pname_pcard_query\\spiders\\verify_code')
                #将正确识别的文件复制到独立目录下
                shutil.copyfile(f"F:\\Pycharm_projects\\pname_pcard_query\\pname_pcard_query\\spiders\\verify_code\\{pic[-1]}", f"F:\\Pycharm_projects\\pname_pcard_query\\pname_pcard_query\\spiders\\True\\{pic[-1]}.jpg")
                form_data = {
                    'captchaId':captchaId,
                    'pCode': pCode,
                    'currentPage': '1',
                    'pCardNum': self.pcardnum,
                    'pName': self.pname,
                    'searchCourtName': '全国法院（包含地方各级法院）',
                    'selectCourtArrange': '1',
                    'selectCourtId': '0'
                }

                yield scrapy.FormRequest(
                        url = form_url,
                        headers = self.headers,
                        formdata = form_data,
                        callback=self.parse,
                        dont_filter=True,
                        meta=form_data,
                )

            else:
                self.start_requests()
                self.index(response)
                self.get_captchaid(response)
                self.check_captcha(response)

        except Exception as e:
            logging.debug(f'*****验证码识别错误异常: {e}*****')

    def parse(self, response):
        item = PnamePcardQueryItem()
        next_page_url = 'http://zxgk.court.gov.cn/xgl/searchXgl.do'
        json_data = response.body_as_unicode()
        if json_data:
            json_data = json.loads(response.body_as_unicode())[0]
            totalsize = json_data["totalSize"]
            #print(f'totalsize:{totalsize}')
            if totalsize:
                pages = json_data['totalPage']
                for page in range(1,pages+1):
                    data = {
                        'captchaId': response.meta['captchaId'],
                        'pCode': response.meta['pCode'],
                        'currentPage': str(page),
                        'pCardNum': self.pcardnum,
                        'pName': self.pname,
                        'searchCourtName': '全国法院（包含地方各级法院）',
                        'selectCourtArrange': '1',
                        'selectCourtId': '0'
                    }
                    #print(data)
                    yield scrapy.FormRequest(
                        url= next_page_url,
                        headers=self.headers,
                        formdata=data,
                        callback=self.parse_detail_page,
                        dont_filter=True,
                    )
            else:
                item['result'] ='未查到相关信息'
                yield item

    #解析json数据
    def parse_detail_page(self,response):
        item = PnamePcardQueryItem()
        try:
            json_data = response.body_as_unicode()
            if json_data:
                json_data = json.loads(json_data)[0]
                data = json_data['result']

                for each in data:
                    each_data = json.loads(each['jsonObject'], strict=False)
                    #print(each_data)

                    # 姓名
                    item['pname'] = each_data["XM"] if "XM" in each_data else ''

                    # 性别
                    item['sex'] = each_data['ZXFYMC'] if 'ZXFYMC' in each_data else ''

                    #身份证号码
                    item['cardnum'] = self.pcardnum

                    # 立案时间
                    item['filing_time'] = each_data['LASJ'] if 'LASJ' in each_data else ''

                    # 案号
                    item['case_num'] = each_data['AH'] if 'AH' in each_data else ''

                    # 企业信息
                    item['enterprise_info'] = each_data['QY_MC'] if 'QY_MC' in each_data else ''

                    yield item

            else:
                print('数据不完整')

        except Exception as e:
            logging.debug(f"*****程序出现异常: {e}*****")

