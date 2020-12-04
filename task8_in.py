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



datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
try :
    with open(str(file), newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
except :
    print("File of the wrong format")
# print(data)

for i in data :
    date = datetime.datetime.strftime(datetime.datetime.strptime(i[0], format),"%Y-%m-%d, %H:%M")

    type = i[1]
    location = i[2]
    vehicle = i[3]
    occupancy = int(i[4])
    # print(date,type,location,vehicle,occupancy)
    count = access_database_with_result('task8.db',
                                            "SELECT COUNT(username) FROM traffic_data \
                                            WHERE traffic_data.username = 'test1' \
                                            AND traffic_data.type = 'add'")
    new_count = count[0][0] + 1






    if type == 'add' :
        access_database('task8.db', "INSERT INTO traffic_data (log,type,location,vehicle,occupancy,datetime,username)\
                                          VALUES ({},'add','{}','{}',{},'{}','test1')".format(new_count,location,vehicle,occupancy,date))
    else :
        log = access_database_with_result('task8.db', "SELECT MAX(log) FROM traffic_data WHERE location = '{}' AND vehicle = '{}'\
                                                  AND occupancy = {} AND type = 'add' AND username = 'test1'".format(location,vehicle,occupancy))
        max_log = log[0][0]


        access_database('task8.db', "UPDATE traffic_data SET log = -1, type = 'undo' WHERE location = '{}' AND\
                                               vehicle = '{}' AND occupancy = {} and log = {}".format(location, vehicle, occupancy,
                                                                                          max_log))


# print(access_database_with_result('task8.db', "SELECT * FROM traffic_data"))