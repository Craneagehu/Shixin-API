#-*- coding:utf-8 -*-
import time

import pname_pcardnum_query
from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer

app = Flask(__name__)


#多线程方式
@app.route('/query/<pname>&<pcardnum>',methods=['GET', 'POST'])
def query(pname,pcardnum):
    if request.method == 'GET':
        name = pname.split('=')[1]
        cardnum = pcardnum.split('=')[1]

        data = pname_pcardnum_query.IndexName().MyThread(name, cardnum)

        if data[0] == "未查到相关信息":
            resp = jsonify({'code':0,'result':data[0]})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

        elif data[0] == '403':
            resp = jsonify({'code': 2, 'result': data})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

        else:
            resp = jsonify({'code':1,'result':data})
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp


#
# #接口方式
# @app.route('/query3/<pname>&<pcardnum>',methods=['GET', 'POST'])
# def query3(pname,pcardnum):
#     # t1 = time.time()
#     if request.method == 'GET':
#         name = pname.split('=')[1]
#         cardnum = pcardnum.split('=')[1]
#         data = pname_pcardnum_query.IndexName().MyThread(name, cardnum)
#
#         if data[0] != "未查到相关信息":
#             resp = jsonify(data)
#             resp.headers['Access-Control-Allow-Origin'] = '*'
#             return resp
#
#         else:
#             resp = jsonify(data[0])
#             resp.headers['Access-Control-Allow-Origin'] = '*'
#             return resp
#




if __name__ == '__main__':

    app.config["JSON_AS_ASCII"] = False
    # app.run(debug=True,host='0.0.0.0',port=5000)
    WSGIServer(('0.0.0.0', 7000), app).serve_forever()
