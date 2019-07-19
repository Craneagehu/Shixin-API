import json
import os
import time
import subprocess
import pname_pcardnum_query
from flask import Flask, request
from gevent.pywsgi import WSGIServer

app = Flask(__name__)


@app.route('/query/<pname>&<pcardnum>',methods=['GET', 'POST'])
def query(pname,pcardnum):
    # t1 = time.time()
    if request.method == 'GET':
        spider_name = 'name_card_query'
        subprocess.check_output(['scrapy', 'crawl', spider_name, '-a', pname, '-a', pcardnum])
        result_bool = os.path.exists('query_info2.json')
        if result_bool:
            with open('./query_info.json',encoding='utf-8') as items_file:
                data = items_file.read()
                # t2 = time.time()
                #print(t2-t1)
                return data
        else:
            return None



@app.route('/query2/<pname>&<pcardnum>',methods=['GET', 'POST'])
def query2(pname,pcardnum):
    # t1 = time.time()
    if request.method == 'GET':
        name = pname.split('=')[1]
        cardnum = pcardnum.split('=')[1]
        data = pname_pcardnum_query.IndexName().MyThread(name, cardnum)

        if data[0] != "未查到相关信息":
            result = {"result": data}
            return json.dumps(result, ensure_ascii=False)
        else:
            result = {"result": data[0]}
            return json.dumps(result, ensure_ascii=False)

if __name__ == '__main__':
    #app.run(debug=True,host='0.0.0.0',port=5000)
    app.config["JSON_AS_ASCII"] = False
    WSGIServer(('0.0.0.0', 5000), app).serve_forever()
