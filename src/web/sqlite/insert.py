#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('ros.db')
c = conn.cursor()
print "Opened database successfully";

c.execute("INSERT INTO amcl (id,type,x,y,w) VALUES (1, 'map' ,1.5, 32.0, 5.6)");

c.execute("INSERT INTO amcl (id,type,x,y,w) VALUES (2, 'base_link' ,1.5, 32.0, 5.6)");

c.execute("INSERT INTO amcl (id,type,x,y,w) VALUES (3, 'pose' ,1.5, 32.0, 5.6)");

c.execute("INSERT INTO amcl (id,type,x,y,w) VALUES (4, 'liscan' ,1.5, 32.0, 5.6)");

conn.commit()
print "Records created successfully";
conn.close()