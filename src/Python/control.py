#!/usr/bin/env python  
# -*- coding: utf-8 -*  

# auth 孙毅明
# 机器人控制程序

import os  
import sys  
import tty, termios  
import roslib 
import rospy  
from geometry_msgs.msg import Twist  
from std_msgs.msg import String  

# bottle
from bottle import run, get, post, request,template,route,static_file,hook,response # or route
# sqlite
import sqlite3
import io,json
# config
import configparser, os,sys
# 进程
from multiprocessing import Process, Pool
global path

path = os.path.split(os.path.abspath(sys.argv[0]))[0] 
running = True

# 跨域访问
@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

def control(cmd,speed,turn):
    global pub
        # roslib.load_manifest('agvsever') 
    # pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)  
    # rospy.init_node('agv_control')  

    # rospy.sleep(2)
    
    # rospy.loginfo('cmd:%s,speed:%s,turn:%s',cmd,speed,turn)

    # rate = rospy.Rate(rospy.get_param('~hz', 3))
    if cmd == 'go':    
        turn = 0  
    elif cmd == 'back':    
        speed = -speed  
        turn = 0     
    elif cmd == 'left':    
        speed = 0
        turn = -turn    
    elif cmd == 'right':    
        speed = 0        
    elif cmd == 'stop':    
        turn = 0  
        speed = 0      
    cmd_vel = Twist() 
    cmd_vel.linear.x = speed
    cmd_vel.angular.z = turn
    # rospy.loginfo('cmd:%s,speed:%s,turn:%s',cmd,speed,turn)
    rospy.loginfo(cmd_vel)
    pub.publish(cmd_vel)  
    # rate.sleep() 

# post参数请求
@post('/')
def control_post():
    # 获取请求类型
    type = request.forms.get('type')
    if  type == 'control':
        cmd = request.forms.get('cmd')
        speed = float(request.forms.get('speed'))
        turn = float(request.forms.get('turn'))
        # # 申请子进程
        # p = Process(target=control, args=(cmd,speed,turn))  
        # # 运行进程
        # p.start()
        control(cmd,speed,turn)
        return '{"resault":true}'


# roslib.load_manifest('agvsever') 

global pub
if __name__ == '__main__':
    # 读取配置
    cp = configparser.ConfigParser()
    str = '../'+path +'/config.ini'
    cp.read('/home/zz/catkin_ws/src/base_controller/web/config.ini')
    print cp.get('control','host')

    pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)  
    rospy.init_node('agv_control')
    rospy.sleep(1)

    # 创建监听
    run(host=cp.get('control','host'), port=cp.get('control','port'), debug=True)
