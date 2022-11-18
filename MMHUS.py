#!/usr/bin/env python
# coding: utf-8

import routeros_api
import mysql.connector
from mysql.connector import errorcode
import logging



def initLogger(name):
    #loggger
    logger = logging.getLogger(name)
    #handlers
    fileHandler = logging.FileHandler('logfile.log')
    fileHandler.setLevel(logging.ERROR)
    #formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    #add handlers
    logger.addHandler(fileHandler)
    return logger

logger = initLogger(__name__)

def getListMysql():
    table="[table]"
    usernames = []
    passwords = []
    
    try:
        #connection to mysql
        cnx = mysql.connector.connect( 
            host='[localhost]',
            user='[user]',
            password='[password]',
            database='[database]'
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
    
    query = ("SELECT username, password FROM {}").format(table)#sql command
    cursor.execute(query)#executing sql
    for (username, password) in cursor:
        usernames.append(username)
        passwords.append(password)
    print('Database query executed successfully')
    return usernames, passwords

def connectMikrotik(ip):
    connect = routeros_api.RouterOsApiPool(ip , username='[username]',password='[password]', plaintext_login=True) #connect to mikrotik
    resource = connect.get_api().get_resource('/ip/hotspot/user')#users from mikrotik
    return resource