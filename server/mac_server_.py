#-*-coding:utf-8 -*-
#for python 3.6.5
import os.path
from flask import Flask,make_response,request,render_template,send_file,send_from_directory,redirect,url_for
import logging
logger = logging.getLogger(__name__)
import json
#import time_transfor
import shutil as su
from datetime import timedelta
import time
import  redis
import pymysql.cursors
import requests

app = Flask(__name__)
app.root_path = os.path.dirname(os.path.abspath(__file__))
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

#auth code start
keys_client = {'fast_login':'brokers:user:{phone}:{process}:code',
        'signup':'brokers:user:{phone}:{process}:code'}
keys_web = {'fast_login':'brokers:user:{phone}:{process}:code',
        'signup':'brokers:user:{phone}:{process}:code',
        'phone_verify':'user:{phone}:{process}:code',
        'email_verify':'user:{phone}:{process}:code',
        'account_verify':'user:{phone}:{process}:code',
        'login_password_verify':'user:{phone}:{process}:code',
        'withdraw_verify':'user:{phone}:{process}:code',
        'email_portal':'brokers:user:{phone}:{process}:code'}

content = {'fast_login':u'获取快速登录验证码',
           'signup':u'获取注册的验证码',
           'phone_verify':u'获取修改手机号验证码',
           'email_verify':u'获取修改邮箱的验证码 ',
           'account_verify':u'获取官网的注册验证码',
           'login_password_verify':u'获取重置登录密码验证码',
           'withdraw_verify':u'获取bos出金的验证码',
           'email_portal':u'邮箱注册验证手机号短信'}

keys_global = {'signup':'verify:{process}:{unique_id}:code',
               'fast_signin':'verify:{process}:{unique_id}:code'}

content_global = {'signup':u'获取国际版APP注册的验证码',
                  'fast_signin':u'获取国际版APP快速登录验证码'}

host_ = '172.30.73.10'
user_ = 'stock_staging'
password_ = 'v8c8gQ_nFK4iN_q2'
db_stock_staging = 'stock_staging'


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        """
        只要检查到了是bytes类型的数据就把它转为str类型
        :param obj:
        :return:
        """
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)

@app.route("/getAuthCodeGlobal",methods=["GET"])
def getAuthCodeGlobal():
    jsonObject = {}
    r=redis.Redis(host='172.30.73.10',port=6379,db=2,password='IeydzcujuhnI25yEdGUz5n14')
    r_ = requests.get("https://test-cms.tigerfintech.com/api/v1/cms/device/info?phone="+request.args.get('phone'))
    result_ = json.loads(r_.text)
    try:
        if result_['data']==[] or ('user_id' in (result_['data'][len(result_['data'])-1]).keys())==False:
            print ("未注册用户")
            for key,value in keys_global.items():
                k=value.format(unique_id=request.args.get('phone'),process=key)
                result=r.get(k)
                jsonObject[content_global[key]] = result
        else:
            print ("已注册用户")
            l = len(result_['data'])
            user_id_ = result_['data'][l-1]['user_id']
            for key,value in keys_global.items():
                k=value.format(unique_id=user_id_,process=key)
                result=r.get(k)
                jsonObject[content_global[key]] = result
    except Exception as e:
        print ("error message==>",e)

    return json.dumps(jsonObject,cls=MyEncoder)
#client
@app.route("/getAuthCode",methods=["GET"])
def getAuthCode():
    jsonObject = {}
    #r=redis.Redis(host='172.30.73.10',port=6379,db=1,password='IeydzcujuhnI25yEdGUz5n14')
    r=redis.Redis(host='172.30.73.10',port=6379,db=2,password='IeydzcujuhnI25yEdGUz5n14')
    for key,value in keys_client.items():
        try:
            k=value.format(phone=request.args.get('phone'),process=key)
            if r.get(k):
                result=r.get(k)
                jsonObject[content[key]] = result
                continue
            #elif r1.get(k):
             #   result=r1.get(k)
             #   jsonObject[content[key]] = result
              #  continue
            else:
                jsonObject[content[key]] = None

        except Exception as e:
            print ("error message==>",e)

    return json.dumps(jsonObject,cls=MyEncoder)
#web
@app.route("/getAuthCodeWeb",methods=["GET"])
def getAuthCodeWeb():
    jsonObject = {}
    r=redis.Redis(host='172.30.73.10',port=6379,db=2,password='IeydzcujuhnI25yEdGUz5n14')
    for key,value in keys_web.items():
        try:
            k=value.format(phone=request.args.get('phone'),process=key)
            result=r.get(k)
            jsonObject[content[key]] = result
        except Exception as e:
            print ("error message==>",e)

    return json.dumps(jsonObject,cls=MyEncoder)

@app.route("/getHkLv2",methods=["GET"])
def getHKLv2():
    try:
        r = requests.get("https://test-cms.tigerfintech.com/api/v1/cms/device/info?phone="+request.args.get('phone'))
        result = json.loads(r.text)
        user_id_ = result['data'][1]['user_id']
    except Exception as e:
        return render_template("test.html",error_message = e)

    #当前日期之后30天
    start_time = '2018-10-16 15:08:33'
    end_time = '2018-10-17 15:08:33'

    connection = pymysql.connect(host=host_,
                                 user=user_,
                                 password=password_,
                                 db=db_stock_staging,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO coupons (user_id,
                                         coupon_start_time,
                                         coupon_end_time,
                                         dates,
                                         coupon_name,
                                         device_scope,
                                         type,
                                         tab,
                                         status) VALUES ("""+str(user_id_)+",'"+start_time+"','"+end_time+"""',1,'test','mobile','hk_quote','quote',1)"""
            cursor.execute(sql)
        connection.commit()
    except Exception as e:
        return render_template("test.html",error_message = e)
    finally:
        connection.close()
    e = "have finished"
    return render_template("test.html",error_message = e)


@app.route("/tools",methods=['GET'])
def tools():
    return render_template("Tools.html")

@app.route("/tools/client/more",methods=['GET'])
def client():
    return render_template('client_more.html')

@app.route("/tools/client_global/more",methods=['GET'])
def client_global():
    return render_template('client_global_more.html')

@app.route("/getResetTradeCode",methods=['GET'])
def resetTradeCode():
    id_number = request.args.get('id_no')
    value = 'oauth:user:{id_no}:trade_pw_reset:code'
    r=redis.Redis(host='172.30.73.10',port=6379,db=1,password='IeydzcujuhnI25yEdGUz5n14')
    try:
        k=value.format(id_no=id_number)
        result=r.get(k)
    except Exception as e:
        print ("error message==>",e)
    return json.dumps({"获取重置交易密码验证码":result},cls=MyEncoder)

#auth code finish

if __name__ == "__main__":
    #app.run(host='0.0.0.0',port=5000,debug=True)
    app.run(host='0.0.0.0',port=5000,threaded=True)
