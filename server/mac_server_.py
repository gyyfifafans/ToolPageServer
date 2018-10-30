#-*-coding:utf-8 -*-
#for python 3.6.5
import os.path
from flask import Flask,make_response,request,render_template,send_file,send_from_directory,redirect,url_for
import logging
logger = logging.getLogger(__name__)
import json
import time_transfor
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
keys = {'fast_login':'brokers:user:{phone}:{process}:code',
        'signup':'brokers:user:{phone}:{process}:code',
        'phone_verify':'user:{phone}:{process}:code',
        'email_verify':'user:{phone}:{process}:code',
        'account_verify':'user:{phone}:{process}:code',
        'login_password_verify':'user:{phone}:{process}:code',
        'withdraw_verify':'user:{phone}:{process}:code',
        'email_portal':'brokers:user:{phone}:{process}:code'}

content = {'fast_login':u'获取APP快速登录验证码',
           'signup':u'获取APP注册的验证码',
           'phone_verify':u'获取修改手机号验证码',
           'email_verify':u'获取修改邮箱的验证码 ',
           'account_verify':u'获取官网的注册验证码',
           'login_password_verify':u'获取重置登录密码验证码',
           'withdraw_verify':u'获取bos出金的验证码',
           'email_portal':u'邮箱注册验证手机号短信'}

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

@app.route("/getAuthCode",methods=["GET"])
def getAuthCode():
    jsonObject = {}
    r=redis.Redis(host='172.30.73.10',port=6379,db=1,password='IeydzcujuhnI25yEdGUz5n14')
    for key,value in keys.items():
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

@app.route('/testReport',methods=['GET'])
def report():
    directory = '/Users/ios_package/.jenkins/jobs'
    filelist = os.listdir(directory)
    fileslist = []
    dirslist = []
    url = {}
    for files in filelist:
        filepath = os.path.join(directory,files)
        if os.path.isdir(filepath):
            if files.startswith("Android") or files.startswith("IOS"):
                dirslist.append(files)
                url[files] = '/detail/'+files
    return render_template("testReport.html",dirsresult = dirslist,urllist = url)


#index.html put in templates dir 
@app.route('/detail/<job_name>',methods=['GET'])
def getDetail(job_name):
    jobDir = '/Users/ios_package/.jenkins/jobs/'
    htmlFileDirectory = jobDir+job_name+'/workspace/reports/html'
    imageFileDirectory = jobDir+job_name+'/workspace/failedcases'
    directory = os.path.split(os.path.realpath(__file__))[0]

    if not os.path.exists(htmlFileDirectory):
        return redirect(url_for("report"))
    
    del_htmlDir(directory)        
    
    #deal with the cache problem
    mytime = str(time.time())
    su.copytree(htmlFileDirectory,directory+'/static/testReport/html'+mytime)
    if os.path.exists(imageFileDirectory):
        su.copytree(imageFileDirectory,directory+'/static/failedcases')
    suite = url_for("static",filename="testReport/html"+mytime+"/suites.html")
    overview = url_for("static",filename="testReport/html"+mytime+"/overview.html")
    return render_template("index.html",s = suite,o = overview)


def del_htmlDir(file_dir):
    #print file_dir
    failcasedirectory = file_dir+'/static'
    htmldirectory = file_dir+'/static/testReport'
    failcaselist = os.listdir(failcasedirectory)
    htmllist = os.listdir(htmldirectory)
    for files in failcaselist:
        filepath = os.path.join(failcasedirectory,files)
        if os.path.isdir(filepath):
            if files.startswith("failedcases"):
                #print 2
                #print files
                su.rmtree(filepath)
    for files in htmllist:
        filepath = os.path.join(htmldirectory,files)
        if os.path.isdir(filepath):
            if files.startswith("html"):
                #print 1
                su.rmtree(filepath)

if __name__ == "__main__":
    #app.run(host='0.0.0.0',port=5000,debug=True)
    app.run(host='0.0.0.0',port=5000,threaded=True)
