# 创建应用实例
import sys

import os
import random
import string
import time

from flask import Flask, request, send_file, render_template, send_from_directory
from string import Template
from werkzeug.utils import secure_filename
from waitress import serve
from concurrent.futures import ThreadPoolExecutor
from wxcloudrun import app

import pdfReader
import swu


app = Flask(__name__)
# 全局变量 共享的文件夹路径 可以根据需求更改
DIRECTORY_PATH = "/pythonFile/tthandler/programme"

app.config['UPLOAD_FOLDER'] = 'upload/'
app.config['DOWNLOAD_FOLDER'] = DIRECTORY_PATH
app.config['ALLOWED_EXTENSIONS'] = set(['pdf'])
app.config['SECURE_KEY'] = 'askydiqyddiudhiudiwuhdhdyjqoijd'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


executor = ThreadPoolExecutor()
swulist_process = []
swulist_num = 6

# For a given file, return whether it's an allowed type or not


def allowed_file(filename):
    """
    检验文件名尾缀是否满足格式要求
    :param filename:
    :return:
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 获取文件信息的函数
def get_files_data():
    files = []
    for i in os.listdir(DIRECTORY_PATH):
        if len(i.split(".")) == 1:  # 判断此文件是否为一个文件夹
            continue

        # 拼接路径
        file_path = DIRECTORY_PATH + "/" + i
        name = i
        size = os.path.getsize(file_path)  # 获取文件大小
        ctime = time.localtime(os.path.getctime(file_path))  # 格式化创建当时的时间戳

        # 列表信息
        files.append({
            "name": name,
            "size": size,
            "ctime": "{}年{}月{}日".format(ctime.tm_year, ctime.tm_mon, ctime.tm_mday),  # 拼接年月日信息
        })
    return files
    
    
def add_new_driver():
    driver = swu.JWXTcookie(None)
    print('新增初始化：', driver)
    swulist_process.append(driver)
    print('初始化chrome池：', swulist_process)


def multiprocess(account, password):
    entertime = int(time.time() * 1000)
    while True:
        nowtime = int(time.time() * 1000)
        if len(swulist_process) > 0:
            driver_temp = swulist_process.pop()
            print('当前请求选定chrome：', driver_temp)
            print('剩余chrome池：', swulist_process)
            returnData = swu.JWXTcookie(driver_temp, account, password)
            executor.submit(lambda p: add_new_driver(*p), [])
            print('请求返回结果：', returnData)
            returnData["time"] = nowtime
            return returnData
            break
        elif nowtime - entertime > 1000 * 20:
            return {
                'state': '当前请求人数过多，已放弃排队',
            }
            break


@app.route("/cpass/JWXTcookie", methods=['POST'])
def JWXTcookie():
    """获取教务系统cookie"""
    account = request.form.getlist("account")
    password = request.form.getlist("password")
    return multiprocess(account, password)

@app.route("/programme/file/<filepath>")
def file_content(filepath):
    """下载文件的URL"""
    print(DIRECTORY_PATH + "/" + filepath)
    if filepath in os.listdir(DIRECTORY_PATH):  # 如果需求下载文件存在
        # 发送文件 参数：文件夹路径，文件路径，文件名
        
        return send_from_directory(directory = DIRECTORY_PATH, path= (DIRECTORY_PATH + '/' + filepath), filename = filepath, as_attachment=True)
    else:
        # 否则返回错误页面
        return 'err'


@app.route("/programme/upload", methods=['POST'])
def programme():
    """上传文件的URL 支持GET/POST请求"""

    if request.method == "POST":
        # 获取文件 拼接存储路径并保存
        upload_file = request.files.get("a1")
        newname = str(int(time.time()*1000)) + upload_file.filename
        upload_file.save(os.path.join(DIRECTORY_PATH, newname))

        # 返回响应报文
        data = {
            'result_desc': 'success',
            'timestamp': '',
            'data': {
                "filepath": newname
            },
        }
        return data

@app.route('/')
def hello_world():
    return 'hello world'


@app.route('/upload', methods=['POST'])
def upload():
    """生成一串指定位数的字符+数组混合的字符串"""
    n = 15
    m = random.randint(1, n)
    a = "".join([str(random.randint(0, 9)) for _ in range(m)])
    b = "".join([random.choice(string.ascii_letters) for _ in range(n - m)])
    file_name = './upload/' + ''.join(random.sample(list(a + b), n)) + '.pdf'
    userTable = {}
    upload_file = request.files['a1']
    if upload_file and allowed_file(upload_file.filename):
        print(file_name)
        upload_file.save(file_name)
        userTable = pdfReader.read(file_name)
        userTable['errCode'] = 0
        return userTable
    else:
        userTable['errCode'] = -1
        return userTable
