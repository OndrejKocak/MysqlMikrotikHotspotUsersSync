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
        return Database(self.parser['mysql'])

    def getDevices(self):
        devicesParsed = self.parser['devices']
        listOfDevices = []
        for device in devicesParsed:
            listOfDevices.append(Device(device))
        return listOfDevices


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
    #username getter
    def getUsername(self):
        return self.username
    #password getter
    def getPassword(self):
        return self.password

    
class Device:
    def __init__(self, deviceDetails):
        self.details = deviceDetails

    def connect(self):
        connect = routeros_api.RouterOsApiPool(self.details["ip"], username=self.details["user"],password=self.details["password"],port=self.details["port"], plaintext_login=True) #connect to mikrotik
        resource = connect.get_api().get_resource('/ip/hotspot/user')#users from mikrotik
        return resource

    def getData(self):
        userListMikrotik = []
        try:
            users = self.connect().get()
            print(users)
            for user in users:
                userListMikrotik.append(user["name"])
            return userListMikrotik
        except routeros_api.exceptions.RouterOsApiConnectionError as err:
            print(err)

class Database:
    def __init__(self, databaseDetails):
        self.details = databaseDetails
    def getData(self):
        table = self.details["table"]
        usernames = self.details["users"]
        passwords = self.details["passwords"]

        #try to connect
        try:
            #connection to mysql
            cnx = mysql.connector.connect( 
                host=self.details["host"],
                user=self.details["username"],
                password=self.details["password"],
                database=self.details["dbName"]
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

        #sql query
        query = ("SELECT {}, {} FROM {}").format(usernames, passwords ,table)

        #executing query
        cursor.execute(query)
        print('Database query executed successfully')

        #parsing data to list
        users = []
        for (username, password) in cursor:
            users.append(User(username, password))
        print('Data from database succesfully added to list')

        return users


if __name__ == "__main__":
    config = Config()
    database = config.getDatabase()
    devices = config.getDevices()
    database.getData()