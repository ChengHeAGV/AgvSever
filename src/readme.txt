#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# auth 孙毅明
from bottle import run, get, post, request,template,route,static_file # or route
import sqlite3
import io,json
import os,sys
# config
import configparser, os,sys

# 根目录
global root
# 当前目录
root = os.path.split(os.path.abspath(sys.argv[0]))[0] 
# 上一级
root = os.path.dirname(root)

# 数据库
conn = sqlite3.connect(root+'/ros.db')

# 读取配置
cp = configparser.ConfigParser()
cp.read(root +'/config.ini')
# 创建监听
run(host=cp.get('comm','host'), port=cp.get('server','port'), debug=bool(cp.get('comm','debug')))



# 运行
# websever
sudo python /home/zz/catkin_ws/src/agvsever/src/web/index.py
