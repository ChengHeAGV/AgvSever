#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# auth 孙毅明
from bottle import run, get, post, request,template,route,static_file # or route
import sqlite3
import io,json
import os,sys

# 当前路径
global path 
path= os.path.split(os.path.abspath(sys.argv[0]))[0] 

# 默认路径
@route("/")  
def index():  
    return template(path+"/html/index.html")   

@route('/html/layui/<filename:path>')  
def layui(filename):  
    return static_file(filename, root=path+'/html/layui/')  

# post参数请求
# @post('/control')
# def control_post():
#     # 获取请求类型
#     type = request.forms.get('type')
#     if  type == 'set_target_pose':
#         x = float(request.forms.get('x'))
#         y = float(request.forms.get('y'))
#         w = float(request.forms.get('w'))
        
#         # t = threading.Thread(target=set_target_pose,args=(x,y,w))
#         # t.start()
#         set_target_pose(x,y,w)

# def set_target_pose(x,y,w):
#     GoToPose(x,y,w)

# post参数请求
@post('/') # or @route('/login', method='POST')
def data_post():
    # 获取请求类型
    type = request.forms.get('type')
    if  type == 'get_amcl_pose':
        return get_amcl_pose()
    elif type == 'get_station':
        return get_station()
    elif type == 'get_task':
        limit = int(request.forms.get('limit'))
        return get_task(limit)
    elif type == 'add_station':
        name = request.forms.get('name')
        x = request.forms.get('x')
        y = request.forms.get('y')
        z = request.forms.get('z')
        w = request.forms.get('w')
        return add_station(name,x,y,z,w)
    elif type == 'change_station':
        id = request.forms.get('id')
        name = request.forms.get('name')
        x = request.forms.get('x')
        y = request.forms.get('y')
        z = request.forms.get('z')
        w = request.forms.get('w')
        return change_station(id,name,x,y,w)
    elif type == 'delete_station':
        id = request.forms.get('id')
        return delete_station(id)

# 获取amcl_pose
def get_amcl_pose():
    type = 'amcl_pose'
    conn = sqlite3.connect(path+'/ros.db')
    c = conn.cursor()
    # 在数据库中查找
    sql = "SELECT * from pose where type='%s'"%type
    # print sql   
    cursor = c.execute(sql)
    cur=cursor.fetchall()

    # print "id = ", cur[0][0]
    # print "type = ", cur[0][1]
    # print "x = ", cur[0][2]
    # print "y = ", cur[0][3]
    # print "w = ", cur[0][4], "\n"

    test = {"x":cur[0][2],"y":cur[0][3],"z":cur[0][4],"w":cur[0][5]}
    python_to_json = json.dumps(test,ensure_ascii=False)
    
    conn.commit()
    # print "Records select successfully"
    conn.close()

    return python_to_json

# 获取站点列表
def get_station():
    conn = sqlite3.connect(path+'/ros.db')
    c = conn.cursor()
    # 在数据库中查找
    sql = "SELECT * from station"
    # print sql   
    cursor = c.execute(sql)
    data = cursor.fetchall()
    jsonData = []
    for row in data:
        result = {} 
        result['id'] = row[0]
        result['name'] = row[1]
        result['x'] = row[2]
        result['y'] = row[3]
        result['z'] = row[4]
        result['w'] = row[5]
        jsonData.append(result)
    
    # print jsonData
    python_to_json = json.dumps(jsonData,ensure_ascii=False, encoding='UTF-8')
    # print python_to_json
    conn.commit()
    # print "Records select successfully"
    conn.close()
    return python_to_json

# 获取任务列表
def get_task(limit):
    conn = sqlite3.connect(path+'/ros.db')
    c = conn.cursor()
    # 在数据库中查找,按订单降序
    sql = "SELECT * from task order by orders desc limit 0,%d"%limit
    # print sql   
    cursor = c.execute(sql)
    data = cursor.fetchall()
    jsonData = []
    for row in data:
        result = {} 
        result['id'] = row[0]
        result['orders'] = row[1]
        result['station'] = row[2]
        result['states'] = row[3]
        result['result'] = row[4]
        result['starts'] = row[5]
        result['stops'] = row[6]
        result['pose'] = row[7]
        jsonData.append(result)

    # print jsonData
    python_to_json = json.dumps(jsonData,ensure_ascii=False, encoding='UTF-8')
    # print python_to_json
    conn.commit()
    # print "Records select successfully"
    conn.close()
    return python_to_json

# 添加站点
def add_station(name,x,y,z,w):
    conn = sqlite3.connect(path+'/ros.db')
    c = conn.cursor()
    # 在数据库中查找
    sql = "INSERT INTO station (name,x,y,z,w) VALUES ('{aa}', '{bb}', '{cc}','{dd}','{ee}')".format(aa=name,bb=x,cc=y,dd=z,ee=w)
    c.execute(sql)
    conn.commit()
    # print "Records save successfully"
    conn.close()
    return '{"resault":true}'

# 更改站点
def change_station(id,name,x,y,z,w):
    conn = sqlite3.connect(path+'/ros.db')
    c = conn.cursor()
    # 在数据库中查找
    sql = "UPDATE station set name='{aa}',x='{bb}',y='{cc}',z='{dd}',w='{ee}' where id='{ff}'".format(aa=name,bb=x,cc=y,dd=z,ee=w,ff=id)
    c.execute(sql)
    conn.commit()
    # print "Records update successfully"
    conn.close()
    return '{"resault":true}'

# 删除站点
def delete_station(id):
    conn = sqlite3.connect(path+'/ros.db')
    c = conn.cursor()
    # 在数据库中查找
    sql = "DELETE FROM station where id='{aa}'".format(aa=id)
    c.execute(sql)
    conn.commit()
    # print "Records delete successfully"
    conn.close()
    return '{"resault":true}'

# run(host='localhost', port=80, debug=True)
run(host='192.168.1.125', port=80, debug=True)
# run(host='192.168.47.128', port=8080, debug=True)