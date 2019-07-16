# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PnamePcardQueryItem(scrapy.Item):

    # 姓名
    pname = scrapy.Field()
    # 性别
    sex = scrapy.Field()
    #身份证号码/组织机构代码
    cardnum = scrapy.Field()
    # 立案时间
    filing_time = scrapy.Field()
    # 案号
    case_num = scrapy.Field()
    # 企业信息
    enterprise_info = scrapy.Field()

    #没有返回信息
    result = scrapy.Field()