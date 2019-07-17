import os
import time
import subprocess
import pname_pcardnum_query
from flask import Flask, request

app = Flask(__name__)


@app.route('/query/<pname>&<pcardnum>',methods=['GET', 'POST'])
def query(pname,pcardnum):
    t1 = time.time()
    if request.method == 'GET':
        spider_name = 'name_card_query'
        subprocess.check_output(['scrapy', 'crawl', spider_name, '-a', pname, '-a', pcardnum])
        result_bool = os.path.exists('query_info2.json')
        if result_bool:
            with open('F:/Pycharm_projects/pname_pcard_query/pname_pcard_query/pname_pcard_flask/query_info.json',encoding='utf-8') as items_file:
                data = items_file.read()
                t2 = time.time()
                print(t2-t1)
                return data
        else:
            return None

@app.route('/query2/<pname>&<pcardnum>',methods=['GET', 'POST'])
def query2(pname,pcardnum):
    t1 = time.time()
    if request.method == 'GET':
        name = pname.split('=')[1]
        cardnum = pcardnum.split('=')[1]
        pname_pcardnum_query.IndexName().MyThread(name, cardnum)

        result_bool = os.path.exists('query_info2.json')
        if result_bool:
            with open('F:/Pycharm_projects/pname_pcard_query/pname_pcard_query/pname_pcard_flask/query_info2.json',encoding='utf-8') as items_file:
                data = items_file.read()
                t2 = time.time()
                #print(t2-t1)
                return data
        else:
            return None

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
