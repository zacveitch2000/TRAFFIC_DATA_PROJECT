import csv
import datetime
import sqlite3
# date = str(201906011243)
#
format = "%Y%m%d%H%M"
# start_date = datetime.datetime.strftime(datetime.datetime.strptime(date, format),"%Y-%m-%d, %H:%M")
def access_database(dbfile, query):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    cursor.execute(query)
    connect.commit()
    connect.close()

# access_database requires the name of a sqlite3 database file and the query.
# It returns the result of the query
def access_database_with_result(dbfile, query):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    rows = cursor.execute(query).fetchall()
    connect.commit()
    connect.close()
    return rows


file = input("please input your csv file (has to be a .csv file otherwise error will be thrown).....")

try :
    with open(str(file), newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
except :
    print("File of the wrong format")
print(data)

for i in data :
    if i[2] == 'login' :
        access_database('task9.db', "INSERT INTO session (username,starttime,logged) VALUES ('{}','{}',1)".format(i[0],datetime.datetime.strftime(datetime.datetime.strptime(i[1], format),"%Y-%m-%d %H:%M")))
    elif i[2] == 'logout' :
        time = datetime.datetime.strftime(datetime.datetime.strptime(i[1], format),"%Y-%m-%d %H:%M")
        access_database('task9.db', "UPDATE session SET logged = 0, endtime = '{}' WHERE username = '{}' AND logged = 1".format(time,i[0]))
print(access_database_with_result('traffic.db', "SELECT * FROM session"))
