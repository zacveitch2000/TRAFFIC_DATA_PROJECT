#!/usr/bin/env python

# This is a simple web server for a traffic counting application.
# It's your job to extend it by adding the backend functionality to support
# recording the traffic in a SQL database. You will also need to support
# some predefined users and access/session control. You should only
# need to extend this file. The client side code (html, javascript and css)
# is complete and does not require editing or detailed understanding.

# import the various libraries needed
import http.cookies as Cookie # some cookie handling support
from http.server import BaseHTTPRequestHandler, HTTPServer # the heavy lifting of the web server
import urllib # some url parsing support
import base64 # some encodin
import sqlite3
import random
import hashlib
import datetime

# This function builds a refill action that allows part of the
# currently loaded page to be replaced.


#Tools needed to edit and do stuff to the sql database
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

def hashing(input) :
    #Function to encode my passwords
    # if type(input) != str :
    #     input = str(input)
    input_encode = input.encode("utf-8")
    hash = hashlib.md5(input_encode)
    hexa = hash.hexdigest()

    return hexa


def setup_traffic_tables(dbfile):
    # Get rid of any existing data
    # everytime the server switches on i want it to empty my tables
    # This is not good practise but for this excercise it will be good for
    # the testing process
    access_database(dbfile, "DROP TABLE IF EXISTS traffic_data")
    access_database(dbfile, "DROP TABLE IF EXISTS user_data")
    access_database(dbfile, "DROP TABLE IF EXISTS session")

    #creating the tables in my database
    access_database(dbfile, "CREATE TABLE traffic_data (log INT, username VARCHAR(255), \
    sessionid VARCHAR(25), type TEXT,\
    location VARCHAR(255), vehicle VARCHAR(255), occupancy INT, datetime DATETIME)")
    access_database(dbfile, "CREATE TABLE user_data (username VARCHAR(15), password VARCHAR(25))")
    access_database(dbfile, "CREATE TABLE session (username VARCHAR(15), sessionid VARCHAR(25), starttime\
     DATETIME, endtime DATETIME, logged INT)")

    # inputting in all the necessary hashed passwords
    access_database(dbfile, "INSERT INTO user_data VALUES ('test1','{}'),('test2','{}'),\
    ('test3','{}'),('test4','{}'),('test5','{}'),\
    ('test6','{}'),('test7','{}'),('test8','{}'),('test9','{}'),\
    ('test10','{}')".format(hashing('password1'), hashing('password2'),\
    hashing('password3'),hashing('password4'),hashing('password5'),hashing('password6'),\
    hashing('password7'),hashing('password8'),\
    hashing('password9'),hashing('password10')))

#Initialising my databases for the different tasks
#If we need clean databases just restart the server
setup_traffic_tables('initial.db')
setup_traffic_tables('task8.db')
setup_traffic_tables('task9.db')


def build_response_refill(where, what):
    text = "<action>\n"

    text += "<type>refill</type>\n"
    text += "<where>"+where+"</where>\n"
    response = base64.b64encode(bytes(what, 'ascii'))
    text += "<what>"+str(response, 'ascii')+"</what>\n"
    text += "</action>\n"
    return text

# This function builds the page redirection action
# It indicates which page the client should fetch.
# If this action is used, only one instance of it should
# contained in the response and there should be no refill action.
def build_response_redirect(where):
    text = "<action>\n"
    text += "<type>redirect</type>\n"
    text += "<where>"+where+"</where>\n"
    text += "</action>\n"
    return text

# This function decides whether a magic token is valid
# Hopefully stopping two users logging in at the same time on the same browser
def handle_validate(iuser, imagic):
    #I want to see if in our SQL table that the
    # sessionid already exists
    result = access_database_with_result('initial.db', "SELECT * \
    FROM session WHERE session.sessionid = '{}'".format(imagic))

    if len(result) == 0 :
        tag = False
    else :
        tag = True
    return tag



## remove the combination of user and magic from the data base, ending the login
def handle_delete_session(iuser, imagic):
    text = "<response>\n"
    #need to logout the old session, find old magic id
    #Want to end the old session
    #need to find the username where the old sessionid stood for
    # old_username = access_database_with_result('initial.db', "SELECT username FROM session WHERE \
    #     sessionid = '{}' AND logged = 1".format(imagic))
    # print("old =", old_username[0][0], type(old_username[0][0]))
    # print(imagic, iuser)
    parameters = 0
    handle_logout_request(iuser,imagic,parameters)
    text += build_response_refill('message', 'Session already in use, try again')
    text += "</response>\n"
    user = ''
    magic = '!'

    return [user,magic,text]

def handle_end_old_session(iuser, imagic, parameters):

    #update this with the time the user logged out
    # time_now = datetime.datetime.\
    #     strptime(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    print("trying to delete old session")
    time_now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
    access_database('initial.db', "UPDATE session SET endtime = '{}'\
     WHERE sessionid = '{}' AND session.username = '{}'".format(time_now,imagic,iuser))
    access_database('initial.db', "UPDATE session SET logged = 0 \
    WHERE username = '{}' AND sessionid = '{}'".format(iuser,imagic))
    # print(access_database_with_result('traffic.db',"SELECT * FROM magic"))
    # print(access_database_with_result('traffic.db', "SELECT * FROM session"))



    text = "<response>\n"
    text += build_response_redirect('/index.html')
    text += build_response_refill('message', 'New Session Live')
    text += "</response>\n"
    user = '!'
    magic = ''

    return [user, magic, text]

## A user has supplied a username (parameters['usernameinput'][0])
## and password (parameters['passwordinput'][0]) check if these are
## valid and if so, create a suitable session record in the database
## with a random magic identifier that is returned.
## Return the username, magic identifier and the response action set.
def handle_login_request(iuser, imagic, parameters):

    # print(type(imagic))
    if handle_validate(iuser, imagic) == True:
        text = "<response>\n"
        # the user is already logged in, so end the existing session.
        handle_delete_session(iuser, imagic)
        text += build_response_refill('message', 'Session already in use, logged all sessions out')


        user = '!'
        magic = ''
        text += "</response>\n"

    else :

    # time_logged_in = datetime.now()

        if 'usernameinput' not in parameters :

            user = '!'
            magic = ''
            text = "<response>\n"
            text += build_response_refill('message', 'Username Missing')
            text += "</response>\n"

        elif 'passwordinput' not in parameters :
            user = '!'
            magic = ''
            text = "<response>\n"
            text += build_response_refill('message', 'Invalid Password')
            text += "</response>\n"

        else :
        #First want to search to see if the username and password are a match in my user_data table
            name = parameters['usernameinput'][0]
            password = parameters['passwordinput'][0]
            # print('imagic =', imagic)
            # print('iuser =', iuser)

            if type(name) != str :
                name = str(name)

            if type(password) != str :
                password = str(password)
            password = hashing(password)
            #check database for matching username and password
            #if length of the match is nothing then we have no matches hence invalid password
            result = access_database_with_result('initial.db', "SELECT * FROM user_data WHERE \
            user_data.username = '{}' AND user_data.password = '{}'".format(name,password))
            search = access_database_with_result('initial.db',
            "SELECT * FROM session WHERE session.username = '{}' \
            AND session.logged = 1".format(name))
            # print('search =', search)
            old_magic  = access_database_with_result('initial.db',
            "SELECT sessionid FROM session WHERE \
            session.username = '{}' AND session.logged = 1".format(name))
            # print(len(search))

            if len(search) > 0 :

                user = name
                magic = str(old_magic[0][0])
                print("new user", iuser, imagic)
                print("old user,", iuser, magic)

                handle_end_old_session(user,magic,parameters)
                text = "<response>\n"


                # print("old stuff -", iuser, old_magic[0][0])


                user = name
                # Generate a magic session token
                magic = random.randint(1, 10000000000000)
                # time_now = datetime.datetime. \
                    # strptime(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                time_now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
                text += build_response_redirect('/page.html')


                access_database('initial.db', "INSERT INTO \
                session (username,sessionid,starttime,logged) VALUES \
                ('{}',{},'{}',1)".format(user,magic,time_now))
                # print(access_database_with_result('traffic.db',"SELECT * FROM session"))
                text += build_response_refill('message', 'Already logged in, Deleted old session')
                text += "</response>\n"


            elif len(result) == 0 :
                text = "<response>\n"
                text += build_response_refill('message', 'Invalid Password')

                user = '!'
                magic = ''
                text += "</response>\n"


            else :
                text = "<response>\n"

                text += build_response_redirect('/page.html')
                user = name
                # Generate a magic session token
                magic = random.randint(1,10000000000000)
                time_now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")


                #Need to update database 'session' table with data
                # username, sessionid, datelogged in

                access_database('initial.db',
                "INSERT INTO session (username,sessionid,starttime,logged) \
                VALUES ('{}','{}','{}',1)".format(user,magic,time_now))
                # print(access_database_with_result('traffic.db', "SELECT * FROM magic"))
                # print(access_database_with_result('initial.db',"SELECT * FROM session"))

                text += "</response>\n"
    return [user, magic, text]

## The user has requested a vehicle be added to the count
## parameters['locationinput'][0] the location to be recorded
## parameters['occupancyinput'][0] the occupant count to be recorded
## parameters['typeinput'][0] the type to be recorded
## Return the username, magic identifier (these can be empty  strings) and the response action set.
def handle_add_request(iuser, imagic, parameters):
    text = "<response>\n"
    if iuser == '' :
        text += build_response_redirect('/index.html')
        text += "</response>\n"
        user = ''
        magic = ''

    elif imagic == '' :
        text += build_response_redirect('/index.html')
        text += "</response>\n"
        user = ''
        magic = ''


    elif handle_validate(iuser, imagic) != True:
        #Invalid sessions redirect to login
        text += build_response_redirect('/index.html')
        text += "</response>\n"
        user = ''
        magic = ''

    elif len(access_database_with_result('initial.db', "SELECT * FROM session WHERE sessionid = {} AND logged = 0".format(imagic))) > 0 :
        text += build_response_refill('message', 'New Session Live')
        text += build_response_redirect('/index.html')

        text += "</response>\n"
        user = ''
        magic = ''




    else: ## a valid session so process the addition of the entry.
        #Not having a location invalid input......
        #Going to try to tackle this using try and except
        if 'locationinput' not in parameters :
            text += build_response_refill('message', 'missing location try again')
            text += "</response>\n"
            user = iuser
            magic = imagic
        else :

            location = parameters['locationinput'][0]
            occupancy = parameters['occupancyinput'][0]
            vehicle = parameters['typeinput'][0]

            # check if non empty and strings
            if parameters['locationinput'][0] == '' :
                text += build_response_refill('message', 'missing location try again')
            elif parameters['occupancyinput'][0] == '' :
                text += build_response_refill('message', 'missing occupancy level try again')
            elif parameters['typeinput'][0] == None :
                text += build_response_refill('message', 'missing vehicle try again')
            else :
                if type(parameters['locationinput'][0]) != str :
                    location = str(parameters['locationinput'][0])
                elif type(parameters['typeinput'][0]) != str :
                    vehicle = str(parameters['typeinput'][0])
                else :
                    # print(location, occupancy, vehicle)
                    count = len(access_database_with_result('initial.db',
                    "SELECT * FROM traffic_data \
                    WHERE traffic_data.username = '{}' AND traffic_data.sessionid = {} \
                    AND traffic_data.type = 'add'".format(iuser,imagic)))
                    new_count = count + 1
                    # time_now = datetime.datetime.strptime(datetime.datetime.today().strftime
                    # ("%Y-%m-%d %H:%M"),"%Y-%m-%d %H:%M")
                    time_now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
                    access_database('initial.db', "INSERT INTO traffic_data \
                    VALUES ({},'{}','{}','add','{}','{}',{},'{}')"\
                    .format(new_count, iuser,imagic, location, vehicle, occupancy, time_now))
                    # print(access_database_with_result('initial.db',"SELECT * FROM traffic_data"))

                    print_count = str(new_count)
            text += build_response_refill('message', 'Entry added.')
            text += build_response_refill('total', print_count)
            text += "</response>\n"
            user = iuser
            magic = imagic

    return [user, magic, text]

## The user has requested a vehicle be removed from the count
## This is intended to allow counters to correct errors.
## parameters['locationinput'][0] the location to be recorded
## parameters['occupancyinput'][0] the occupant count to be recorded
## parameters['typeinput'][0] the type to be recorded
## Return the username, magic identifier (these can be empty  strings) and the response action set.
def handle_undo_request(iuser, imagic, parameters):
    # # old_session = access_database_with_result('initial.db', "SELECT * FROM session WHERE sessionid = {} AND logged = 0".format(imagic))
    # is_there_anything = access_database_with_result('initial.db', "SELECT * FROM traffic_data WHERE sessionid = {}".format(imagic))
    text = "<response>\n"

    if iuser == '':
        text += build_response_redirect('/index.html')
        text += "</response>\n"
        user = ''
        magic = ''

    elif imagic == '':
        text += build_response_redirect('/index.html')
        text += "</response>\n"
        user = ''
        magic = ''


    elif handle_validate(iuser, imagic) != True:
        #Invalid sessions redirect to login
        text += build_response_redirect('/index.html')
        user = ''
        magic = ''

    elif len(access_database_with_result('initial.db', "SELECT * FROM session WHERE sessionid = {} AND logged = 0".format(imagic))) > 0:
        text += build_response_refill('message', 'New Session Live')
        text += build_response_redirect('/index.html')
        user = ''
        magic = ''

    elif len(access_database_with_result('initial.db', "SELECT * FROM traffic_data WHERE sessionid = {}".format(imagic))) == 0 :
        text += build_response_refill('message', 'Nothing to undo')
        user = iuser
        magic = imagic



    else: ## a valid session so process the recording of the entry.
        #the max log value in the table is the most recent one so thats the one we undo
        if 'locationinput' in parameters :
            if 'occupancyinput' in parameters :
                if 'typeinput' in parameters :


                    try :
                        location = parameters['locationinput'][0]
                        occupancy = parameters['occupancyinput'][0]
                        vehicle = parameters['typeinput'][0]
                        log = access_database_with_result('initial.db',
                            "SELECT MAX(log) FROM traffic_data \
                            WHERE traffic_data.location = '{}' AND traffic_data.username = '{}' \
                            AND traffic_data.sessionid = {} \
                            AND traffic_data.vehicle = '{}'\
                            AND traffic_data.occupancy = {} AND type = 'add'"
                            .format(location,iuser,imagic,vehicle,occupancy))
                        new_log = log[0][0]
                        access_database('initial.db', "UPDATE traffic_data SET log = -1, type = 'undo' \
                            WHERE traffic_data.log = {} AND traffic_data.username = '{}' \
                            AND traffic_data.sessionid = {}".format(new_log,iuser,imagic))
                        max_log = access_database_with_result('initial.db', "SELECT COUNT(log) \
                            FROM traffic_data WHERE traffic_data.username = '{}' \
                            AND traffic_data.sessionid = {} AND traffic_data.type = 'add' \
                            AND traffic_data.log > 0".format(iuser,imagic))
                        log = max_log[0][0]

                        text += build_response_refill('message', 'Entry Un-done.')
                        text += build_response_refill('total', str(log))
                        user = iuser
                        magic = imagic

                    except :
                        text += build_response_refill('message', 'Never Recorded that entry')
                        user = iuser
                        magic = imagic

        # else :
        #     #remove the last entry added in if no location is provided
        #     max_log = access_database_with_result('initial.db',"SELECT MAX(log)\
        #      FROM traffic_data WHERE \
        #     traffic_data.username = '{}' AND traffic_data.sessionid = {} AND \
        #     traffic_data.type = 'add' AND traffic_data.log > 0".format(iuser, imagic))
        #     log = max_log[0][0]
        #     access_database('initial.db', "UPDATE traffic_data SET log = -1, type = 'undo' WHERE \
        #     traffic_data.log = {} AND traffic_data.username = '{}' \
        #     AND traffic_data.sessionid = {}".format(log, iuser, imagic))
        #     new_log = log - 1
        #     text += build_response_refill('message', 'Last entry Un-done.')
        #     text += build_response_refill('total', str(new_log))
        #     user = iuser
        #     magic = imagic

    text += "</response>\n"

    return [user, magic, text]

# This code handles the selection of the back button on the record form (page.html)
# You will only need to modify this code if you make changes elsewhere that break its behaviour
def handle_back_request(iuser, imagic, parameters):
    old_session = access_database_with_result('initial.db', "SELECT * FROM session WHERE sessionid = {} AND logged = 0".format(imagic))

    text = "<response>\n"
    if handle_validate(iuser, imagic) != True:
        text += build_response_redirect('/index.html')
        user = ''
        magic = ''
    elif len(old_session) > 0:
        text += build_response_refill('message', 'New Session Live')
        text += build_response_redirect('/index.html')
        user = ''
        magic = ''
    else:
        text += build_response_redirect('/summary.html')
        user = iuser
        magic = imagic


    text += "</response>\n"

    return [user, magic, text]

## This code handles the selection of the logout button on the summary page (summary.html)
## You will need to ensure the end of the session is recorded in the database
## And that the session magic is revoked.
def handle_logout_request(iuser, imagic, parameters):
    #update this with the time the user logged out
    # time_now = datetime.datetime.\
    #     strptime(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    time_now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M")
    access_database('initial.db', "UPDATE session SET endtime = '{}'\
     WHERE sessionid = '{}' AND session.username = '{}'".format(time_now,imagic,iuser))
    access_database('initial.db', "UPDATE session SET logged = 0 \
    WHERE username = '{}' AND sessionid = '{}'".format(iuser,imagic))
    # print(access_database_with_result('traffic.db',"SELECT * FROM magic"))
    # print(access_database_with_result('traffic.db', "SELECT * FROM session"))
    text = "<response>\n"
    text += build_response_redirect('/index.html')
    user = '!'
    magic = ''
    text += "</response>\n"
    return [user, magic, text]

## This code handles a request for update to the session summary values.
## You will need to extract this information from the database.
def handle_summary_request(iuser, imagic, parameters):
    old_session = access_database_with_result('initial.db', "SELECT * FROM session WHERE sessionid = {} AND logged = 0".format(imagic))

    text = "<response>\n"
    if handle_validate(iuser, imagic) != True:
        text += build_response_redirect('/index.html')
        text += "</response>\n"

    elif len(old_session) > 0:
        text += build_response_refill('message', 'New Session Live')
        text += build_response_redirect('/index.html')


    else:

        car = access_database_with_result('initial.db', "SELECT COUNT(username) FROM traffic_data \
        WHERE traffic_data.username = '{}' AND traffic_data.vehicle = 'car' AND \
        traffic_data.type = 'add' AND traffic_data.sessionid = {}".format(iuser, imagic))
        taxi = access_database_with_result('initial.db', "SELECT COUNT(username) FROM traffic_data\
         WHERE traffic_data.username = '{}' AND traffic_data.vehicle = 'taxi' \
         AND traffic_data.type = 'add' AND traffic_data.sessionid = {}".format(iuser, imagic))
        bus = access_database_with_result('initial.db', "SELECT COUNT(username) FROM traffic_data \
        WHERE traffic_data.username = '{}' \
        AND traffic_data.vehicle = 'bus' \
        AND traffic_data.type = 'add' \
        AND traffic_data.sessionid = {}".format(iuser, imagic))
        motorbike = access_database_with_result('initial.db',
        "SELECT COUNT(username) FROM traffic_data \
        WHERE traffic_data.username = '{}' AND traffic_data.vehicle = 'motorbike' \
        AND traffic_data.type = 'add'AND traffic_data.sessionid = {}".format(iuser, imagic))
        bicycle = access_database_with_result('initial.db', "SELECT COUNT(username) FROM traffic_data \
        WHERE traffic_data.username = '{}' AND traffic_data.vehicle = 'bicycle'\
         AND traffic_data.type = 'add' \
         AND traffic_data.sessionid = {}".format(iuser, imagic))
        van = access_database_with_result('initial.db', "SELECT COUNT(username) FROM traffic_data \
        WHERE traffic_data.username = '{}' AND traffic_data.vehicle = 'van' \
        AND traffic_data.type = 'add' AND traffic_data.sessionid = {}".format(iuser, imagic))
        truck = access_database_with_result('initial.db', "SELECT COUNT(username) FROM traffic_data \
        WHERE traffic_data.username = '{}' AND traffic_data.vehicle = 'truck'\
         AND traffic_data.type = 'add' AND traffic_data.sessionid = {}".format(iuser, imagic))
        other = access_database_with_result('initial.db', "SELECT COUNT(username) FROM traffic_data \
        WHERE traffic_data.username = '{}' AND traffic_data.vehicle = 'other'\
         AND traffic_data.type = 'add' AND traffic_data.sessionid = {}".format(iuser, imagic))
        count_car = car[0][0]
        count_taxi = taxi[0][0]
        count_bus = bus[0][0]
        count_mb = motorbike[0][0]
        count_bicy = bicycle[0][0]
        count_van = van[0][0]
        count_truck = truck[0][0]
        count_other = other[0][0]
        count_total = count_car + count_taxi + count_bus + count_mb \
                      + count_bicy + count_van + count_truck + count_other

        text += build_response_refill('sum_car', str(count_car))
        text += build_response_refill('sum_taxi', str(count_taxi))
        text += build_response_refill('sum_bus', str(count_bus))
        text += build_response_refill('sum_motorbike', str(count_mb))
        text += build_response_refill('sum_bicycle', str(count_bicy))
        text += build_response_refill('sum_van', str(count_van))
        text += build_response_refill('sum_truck', str(count_truck))
        text += build_response_refill('sum_other', str(count_other))
        text += build_response_refill('total', str(count_total))
        text += "</response>\n"
        user = iuser
        magic = imagic
    return [user, magic, text]


# HTTPRequestHandler class
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET This function responds to GET requests to the web server.
    def do_GET(self):

        # The set_cookies function adds/updates two cookies returned with a webpage.
        # These identify the user who is logged in. The first parameter identifies the user
        # and the second should be used to verify the login session.
        def set_cookies(x, user, magic):
            ucookie = Cookie.SimpleCookie()
            ucookie['u_cookie'] = user
            x.send_header("Set-Cookie", ucookie.output(header='', sep=''))
            mcookie = Cookie.SimpleCookie()
            mcookie['m_cookie'] = magic
            x.send_header("Set-Cookie", mcookie.output(header='', sep=''))

        # The get_cookies function returns the values of the user and magic cookies if they exist
        # it returns empty strings if they do not.
        def get_cookies(source):
            rcookies = Cookie.SimpleCookie(source.headers.get('Cookie'))
            user = ''
            magic = ''
            for keyc, valuec in rcookies.items():
                if keyc == 'u_cookie':
                    user = valuec.value
                if keyc == 'm_cookie':
                    magic = valuec.value
            return [user, magic]

        # Fetch the cookies that arrived with the GET request
        # The identify the user session.
        user_magic = get_cookies(self)

        print(user_magic)

        # Parse the GET request to identify the file requested and the GET parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # Return a CSS (Cascading Style Sheet) file.
        # These tell the web client how the page should appear.
        if self.path.startswith('/css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return a Javascript file.
        # These tell contain code that the web client can execute.
        if self.path.startswith('/js'):
            self.send_response(200)
            self.send_header('Content-type', 'text/js')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # A special case of '/' means return the index.html (homepage)
        # of a website
        elif parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./index.html', 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return html pages.
        elif parsed_path.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('.'+parsed_path.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # The special file 'action' is not a real file, it indicates an action
        # we wish the server to execute.
        elif parsed_path.path == '/action':
            self.send_response(200) #respond that this is a valid page request
            # extract the parameters from the GET request.
            # These are passed to the handlers.
            parameters = urllib.parse.parse_qs(parsed_path.query)
            # print(parameters)

            if 'command' in parameters:
                # check if one of the parameters was 'command'
                # If it is, identify which command and call the appropriate handler function.
                if parameters['command'][0] == 'login':
                    [user, magic, text] = handle_login_request(user_magic[0], user_magic[1], parameters)
                    #The result to a login attempt will be to set
                    #the cookies to identify the session.
                    set_cookies(self, user, magic)
                elif parameters['command'][0] == 'add':
                    [user, magic, text] = handle_add_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'undo':
                    [user, magic, text] = handle_undo_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'back':
                    [user, magic, text] = handle_back_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'summary':
                    [user, magic, text] = handle_summary_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'logout':
                    [user, magic, text] = handle_logout_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                else:
                    # The command was not recognised, report that to the user.
                    text = "<response>\n"
                    text += build_response_refill('message', 'Internal Error: Command not recognised.')
                    text += "</response>\n"

            else:
                # There was no command present, report that to the user.
                text = "<response>\n"
                text += build_response_refill('message', 'Internal Error: Command not found.')
                text += "</response>\n"
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(bytes(text, 'utf-8'))
        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)
            self.end_headers()
        return

# This is the entry point function to this code.
def run():
    print('starting server...')
    ## You can add any extra start up code here
    # Server settings
    # Choose port 8081 over port 80, which is normally used for a http server
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever() # This function will not return till the server is aborted.

run()
