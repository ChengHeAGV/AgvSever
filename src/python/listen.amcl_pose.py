#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped,PoseStamped

import sqlite3
import io,json,os,sys

# config
import configparser, os,sys

# 根目录
global root
# 当前目录
root = os.path.split(os.path.abspath(sys.argv[0]))[0] 
# 上一级
root = os.path.dirname(root)

def callback(msg):
    data=""
    #订阅到的坐标信息
    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y
    #订阅到的四元数的信息，用来表示朝向
    orien_z = msg.pose.pose.orientation.z
    orien_w = msg.pose.pose.orientation.w

    rospy.loginfo("position_x:%s",x)
    rospy.loginfo("position_y:%s",y)
    rospy.loginfo("orientation_z:%s",orien_z)
    rospy.loginfo("orientation_w:%s",orien_w)

    # 写入数据库
    conn = sqlite3.connect(root+'/ros.db')
    c = conn.cursor()
    # 在数据库中查找
    sql = "UPDATE pose set x='{aa}',y='{bb}',z='{cc}',w='{dd}' where type='amcl_pose'".format(aa=x,bb=y,cc=orien_z,dd=orien_w)
    # print sql
    c.execute(sql)
    conn.commit()
    conn.close()
    print "listen.py"
    
def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("amcl_pose", PoseWithCovarianceStamped, callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()