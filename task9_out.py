import sqlite3
import csv
import datetime

date = input("Input the start date + time in the form YYYYMMdd : ")
format = "%Y%m%d"
try :
    date = datetime.datetime.strptime(date, format)
    day_date = date + datetime.timedelta(days=1)
    week_date = date - datetime.timedelta(days=6)
    date = datetime.datetime.strftime(date, "%Y-%m-%d %H:%M")
    day_date = datetime.datetime.strftime(day_date, "%Y-%m-%d %H:%M")
    week_date = datetime.datetime.strftime(week_date, "%Y-%m-%d %H:%M")
except :
    print("Invalid Date")


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
# (julianday(endtime) - julianday(starttime) * 24)

# SELECT (julianday(CURRENT_TIMESTAMP) - julianday(my_timestamp)) * 86400.0) FROM my_table;
# FIND the total number of hours on a given day
# print(date)
# print(day_date)
# print(date, week_date, day_date)

final_list = []
users = ['test1','test2','test3','test4','test5','test6','test7','test8','test9','test10']


for user in users :


    check = access_database_with_result('task9.db', "SELECT * FROM session\
                                                      WHERE username = '{}' AND \
                                                      (starttime BETWEEN date('{}', '-1 months') AND '{}') AND (endtime BETWEEN date('{}', '-1 months') AND '{}')".format(user,day_date,day_date,day_date,day_date))
    if len(check) > 0 :
        new_list = []
        day = access_database_with_result('task9.db', "SELECT ROUND(SUM(((julianday(endtime) - julianday(starttime)) * 24)),1) FROM session\
                                          WHERE username = '{}' AND \
                                        (starttime BETWEEN '{}' AND '{}') AND (endtime BETWEEN '{}' AND '{}')".format(user,date,day_date,date,day_date))

        week = access_database_with_result('task9.db.db', "SELECT ROUND(SUM(((julianday(endtime) - julianday(starttime)) * 24)),1) FROM session\
                                          WHERE username = '{}' AND\
                                        (starttime BETWEEN '{}' AND '{}') AND (endtime BETWEEN '{}' AND '{}')".format(user,week_date,day_date,week_date,day_date))

        month = access_database_with_result('task9.db', "SELECT ROUND(SUM(((julianday(endtime) - julianday(starttime)) * 24)),1) FROM session\
                                                  WHERE username = '{}' AND \
                                                (starttime BETWEEN date('{}', '-1 months') AND '{}') AND (endtime BETWEEN date('{}', '-1 months') AND '{}')".format(user,day_date,day_date,day_date,day_date))
        #accounting for time negligable time gaps
        try :
            new_list.append(user)
            new_list.append(day[0][0])
            new_list.append(week[0][0])
            new_list.append(month[0][0])
            final_list.append(new_list)
        except :
            continue

with open("task9_out.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(final_list)