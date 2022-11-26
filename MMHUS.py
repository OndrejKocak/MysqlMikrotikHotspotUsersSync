#!/usr/bin/env python
# coding: utf-8

import routeros_api
import mysql.connector
from mysql.connector import errorcode

import yaml


class Config:
    file_path = "config.yaml"
    def __init__(self):
        with open(self.file_path, "r") as f:
            self.parser = yaml.safe_load(f)

    def getDatabase(self):
        return self.parser['mysql']

    def getDevices(self):
        return self.parser['devices']

    




def getListMysql(database):
    table = database["table"]
    usernames = database["users"]
    passwords = database["passwords"]
    
    try:
        #connection to mysql
        cnx = mysql.connector.connect( 
            host=database["host"],
            user=database["username"],
            password=database["password"],
            database=database["dbName"]
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

def connectMikrotik(device):
    connect = routeros_api.RouterOsApiPool(device["ip"], username=device["user"],password=device["password"],port=device["port"], plaintext_login=True) #connect to mikrotik
    resource = connect.get_api().get_resource('/ip/hotspot/user')#users from mikrotik
    return resource

if __name__ == "__main__":
    config = Config()
    database = config.getDatabase()
    devices = config.getDevices()
    '''
    print(config.getDatabase(),'\n', devices)

    for device in devices:
        print(device["ip"])
    '''