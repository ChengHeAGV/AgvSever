# By Vamei
import sqlite3

# ros.db is a file in the working directory.
conn = sqlite3.connect("ros.db")

c = conn.cursor()

# create tables

c.execute('''CREATE TABLE amcl
      (id int primary key, 
       type text,
       x float, 
       y float, 
       w float)''')

# save the changes
conn.commit()

# close the connection with the database
conn.close()