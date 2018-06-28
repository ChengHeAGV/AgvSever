#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# auth 孙毅明
# TurtleBot must have minimal.launch & amcl_demo.launch
# Order prior to starting this script
# For simulation: launch gazebo world & amcl_demo prior to run this script

# ros
import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion

import time
# 进程
from multiprocessing import Process, Pool
# bottle
from bottle import run, get, post, request,template,route,static_file,hook,response # or route
# sqlite
import sqlite3
import io,json
# config
import configparser, os,sys

# 功能描述
# 监控post来的目标位置，并返回响应结果（之前是否有任务，有任务则自动取消）
# 在数据库创建该任务，标记之前任务执行结果（被取消），标记当前任务（正在执行）
# 任务执行完成后更新数据库执行结果（完成，执行失败，成功，到达指定位置）

# config
import configparser, os,sys

# 根目录
global root
# 当前目录
root = os.path.split(os.path.abspath(sys.argv[0]))[0] 
# 上一级
root = os.path.dirname(root)


# 跨域访问
@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

class GoTo():
    def __init__(self,index):
        self.goal_sent = False
        self.goal_cancel = False
        self.index = index

	# What to do if shut down (e.g. Ctrl-C or failure)
	rospy.on_shutdown(self.shutdown)
	
	# Tell the action client that we want to spin a thread by default
	self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
	rospy.loginfo("[%s]等待服务器[5秒]..."%self.index)

	# Allow up to 5 seconds for the action server to come up
	self.move_base.wait_for_server(rospy.Duration(5))

    def goto(self, pos, quat):
        # Send a goal
        self.goal_sent = True
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(pos['x'], pos['y'], 0.000),Quaternion(quat['r1'], quat['r2'], quat['r3'], quat['r4']))

	# Start moving
        self.move_base.send_goal(goal)

	# Allow TurtleBot up to 60 seconds to complete task
	rospy.loginfo("[%s]等待执行结果[10秒]..."%self.index)
	success = self.move_base.wait_for_result(rospy.Duration(10)) 
        state = self.move_base.get_state()
        rospy.loginfo("[%s]执行状态：%s",self.index,state)
        result = False
        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False
        return result

    def shutdown(self):
        if self.goal_sent:
            self.move_base.cancel_goal()
        rospy.loginfo("[%s]强制取消任务",self.index)
        # 标记任务被取消
        self.goal_cancel = True
        rospy.sleep(1)

def GoToPose(x,y,z,w,index):
    try:
        rospy.init_node('nav_test', anonymous=False)
        navigator = GoTo(index)
        # Customize the following values so they are appropriate for your location
        position = {'x': x, 'y' : y}
        quaternion = {'r1' : 0.000, 'r2' : 0.000, 'r3' : z, 'r4' : w}
        rospy.loginfo("[%s] Go to (x:%s, y:%s, z:%s, w:%s)",index, position['x'], position['y'],quaternion['r3'],quaternion['r4'])
        success = navigator.goto(position, quaternion)

        result = False
        state = 'finished'
        if success:
            rospy.loginfo("[%s]执行成功，到达指定位置",index)
            result = True
        elif navigator.goal_cancel:
            rospy.loginfo("[%s]执行失败，任务被取消"%index)
            state = 'cancelled'
        else:
            rospy.loginfo("[%s]执行失败，未达指定位置"%index)

        # 更新数据库
        conn = sqlite3.connect(root+'/ros.db')
        c = conn.cursor()
        # 更新数据库
        sql = "UPDATE task set states='{aa}',result='{bb}',stops='{cc}' where orders='{dd}'".format(aa=state,bb=result,cc=int(time.time()),dd=index)
        # print sql
        c.execute(sql)
        conn.commit()
        conn.close()

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)
    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting-%s"%index)


# post参数请求
@post('/goto')
def control_post():
    # 获取请求类型
    type = request.forms.get('type')
    if  type == 'goto_pose':
        order = request.forms.get('order')
        station = request.forms.get('station')
        x = float(request.forms.get('x'))
        y = float(request.forms.get('y'))
        z = float(request.forms.get('z'))
        w = float(request.forms.get('w'))
        # 申请子进程
        p = Process(target=GoToPose, args=(x,y,z,w,order))  
        # 运行进程
        p.start()

        # 存入数据库
        conn = sqlite3.connect(root+'/ros.db')
        c = conn.cursor()
        # 组装位姿
        pose = '{"x":%s,"y":%s,"z":%s,"w":%s}'%(x,y,z,w)
        # 插入数据库
        sql = "INSERT INTO task (orders,station,states,starts,pose) VALUES ('{aa}','{bb}', '{cc}','{dd}','{ee}')".format(aa=order,bb=station,cc='running',dd=int(time.time()),ee=pose)
        # print sql
        c.execute(sql)
        conn.commit()
        conn.close()
        return '{"resault":true}'

if __name__ == '__main__':
    # 读取配置
    cp = configparser.ConfigParser()
    cp.read(root +'/config.ini')
    # 创建监听
    run(host=cp.get('comm','host'), port=cp.get('goto','port'), debug=bool(cp.get('comm','debug')))



# p1 = Process(target=GoToPose, args=(1.88,0.098,0.018))  #申请子进程
# p1.start()#运行进程
# print "Parent process run. subProcess is ", p1.pid
# print "Parent process end,{0}".format(time.ctime())

# time.sleep(3)
# p2 = Process(target=GoToPose, args=(2.88,2.098,2.018))  #申请子进程
# p2.start()#运行进程
# print "Parent process run. subProcess is ", p2.pid
# print "Parent process end,{0}".format(time.ctime())

# Parent process run. subProcess is  8507
# Parent process end,Fri Jun 22 11:57:32 2018
# [INFO] [1529639853.153829]: Wait for the action server to come up-1
# Parent process run. subProcess is  8527
# Parent process end,Fri Jun 22 11:57:36 2018
# [INFO] [1529639856.166569]: Wait for the action server to come up-2
# shutdown request: new node registered with same name
# [INFO] [1529639856.208193]: Stop-1
# [INFO] [1529639857.219198]: Go to (x:1.88, y:0.098, w:0.018) pose -1
# [INFO] [1529639857.219449]: navigator.goto-1
# [INFO] [1529639857.219805]: 完成-1
# [INFO] [1529639857.219970]: The base failed to reach the desired pose-1
# [INFO] [1529639861.176473]: Go to (x:2.88, y:2.098, w:2.018) pose -2
# [INFO] [1529639861.176764]: navigator.goto-2
# [INFO] [1529639871.178118]: 完成-2
# [INFO] [1529639871.178557]: The base failed to reach the desired pose-2

