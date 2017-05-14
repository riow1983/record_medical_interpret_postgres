import sqlite3

conn = sqlite3.connect('database.db')
print("Opened database successfully")

conn.execute('CREATE TABLE report (personnel TEXT, starttime DATETIME, endtime DATETIME, client TEXT, section TEXT, patient TEXT, country TEXT, summary TEXT)')
print("Table created successfully")
conn.close()