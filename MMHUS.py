#!/usr/bin/env python
# coding: utf-8

import routeros_api
import mysql.connector
from mysql.connector import errorcode
import logging


class Logger:
    #loggger
    logger = logging.getLogger('__name__')
    #handlers
    fileHandler = logging.FileHandler('logfile.log')
    fileHandler.setLevel(logging.ERROR)
    #formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    #add handlers
    logger.addHandler(fileHandler)

def getListMysql(region):
    usernames = []
    passwords = []
    try:
        #connection to mysql
        cnx = mysql.connector.connect( 
            host='localhost',
            user='root',
            password='Autobus1+',
            database='hugo'
            )
        print('Connected to Database')
         # catch errors when connection is starting
    except mysql.connector.Error as err: 
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password to Database")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
            

    cursor = cnx.cursor()
    
    query = ("SELECT username, unique_id FROM users WHERE id IN (SELECT user_id FROM region_user WHERE region_id={}) AND active=1").format(region)#sql command
    cursor.execute(query)#executing sql
    for (username, unique_id) in cursor:
        usernames.append(username)
        passwords.append(unique_id)
    print('Database query executed successfully')
    return usernames, passwords