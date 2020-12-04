import csv
import sqlite3
import datetime

start_date = input("Input the start date + time in the form YYYY-MM-dd, hh:mm :")
format = "%Y-%m-%d, %H:%M"
try :
    start_date = datetime.datetime.strptime(start_date, format)
except :
    print("Invalid Date")
    start_date = input("Input the start date + time in the form YYYY-MM-dd, hh:mm ")

end_date = input("Input the end date + time in the form YYYY-MM-dd, hh:mm :")
try :
    end_date = datetime.datetime.strptime(end_date, format)
except :
    print("Invalid Date")
    end_date = input("Input the end date + time in the form YYYY-MM-dd, hh:mm ")



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

# print(access_database_with_result('traffic.db', "SELECT * FROM traffic_data WHERE (datetime BETWEEN '{}' AND '{}')".format(start_date,end_date)))

location = access_database_with_result('task8.db', "SELECT location FROM traffic_data WHERE type = 'add' AND (datetime BETWEEN '{}' AND '{}') GROUP BY location".format(start_date,end_date))
location_list = []
for i in location :
    location_list.append(i[0])
vehicle_list = ['car','bus','taxi','bicycle','motorbike','van','truck','other']
occ = [1,2,3,4]
final_list = []
for loc in location_list :
    for veh in vehicle_list :
        loc_veh = []
        loc_veh.append(loc)
        loc_veh.append(veh)
        count_list = []
        for i in occ :
            count = access_database_with_result('task8.db', "SELECT COUNT(occupancy) FROM traffic_data WHERE \
                                               location = '{}' AND vehicle = '{}' AND occupancy = {} AND type = 'add'\
                                                              AND (datetime BETWEEN '{}' AND '{}')".format(loc,veh,i,start_date,end_date))
            count_list.append(count[0][0])
        # print(count_list)
        if all([v == 0 for v in count_list]):
            continue
        else :
            final_list.append(loc_veh + count_list)

with open("task8_out.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(final_list)


