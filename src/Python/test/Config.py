#!/usr/bin/env python
#-*- coding: utf-8 -*-
# auth 孙毅明

import configparser, os,sys

global path 
path= os.path.split(os.path.abspath(sys.argv[0]))[0] 

def func():
    # global path
    cp = configparser.ConfigParser()
    print path
    str = path +'/config.ini'
    print str
    cp.read(str)

    print 'mongodb host',cp.get('mongodb','host')
    print 'kafka bootstrap_servers',cp.get('kafka','bootstrap_servers')
    print 'log file name',cp.get('log','log_file_name')
    print 'zookeeper conn string',cp.get('zookeeper','conn_str')

if __name__ == '__main__':
    func()
    # print os.path.split(os.path.abspath(sys.argv[0])) 