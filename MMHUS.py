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
    #load database info from config
    def getDatabase(self):
        return Database(self.parser['mysql'])
    #load devices information from config
    def getDevices(self):
        devicesParsed = self.parser['devices']
        listOfDevices = []
        for device in devicesParsed:
            listOfDevices.append(Device(device))
        return listOfDevices


class User:
    def __init__(self, username, password, id=None):
        self.username = username
        self.password = password
        self.id = id
    # == overloading
    def __eq__(self, other):
        if(self.username == other.username):
            return True
        return False

    
class Device:
    def __init__(self, deviceDetails):
        self.details = deviceDetails
        self.resource = self.connect()

    #connect to device
    def connect(self):
        try:
            self.connection = routeros_api.RouterOsApiPool(self.details["ip"], username=self.details["user"],password=self.details["password"],port=self.details["port"], plaintext_login=self.details["plainTextLogin"]) #connect to mikrotik
            resource = self.connection.get_api().get_resource('/ip/hotspot/user')#users from mikrotik
        except routeros_api.exceptions.RouterOsApiConnectionError as err:
            print(err)
        return resource

    #disconnect from device    
    def __del__(self):
        self.connection.disconnect()

    #get  users from device
    def getData(self):
        userListMikrotik = []
        users = self.resource.get()
        for user in users:
            if user['id'] != "*0":
                userListMikrotik.append(User(user["name"], user["password"], user['id']))  
        return userListMikrotik

    #check if password was changed
    def __checkPasswordChange(self, dbUser, mtUser):
        if(dbUser.password != mtUser.password):
            self.resource.set(id=mtUser.id, password=dbUser.password)

    #checks not added users
    def checkNotAdded(self, database):
        users = self.getData()
        for dbUser in database.users:
            added = False
            for mtUser in users:
                if(dbUser == mtUser):
                    added = True
                    self.__checkPasswordChange(dbUser, mtUser)       
            if(added == False):
                self.resource.add(name=dbUser.username, password=dbUser.password)

    #checks for removed users
    def checkRemoved(self, database):
        users = self.getData()
        for user in users:
            if(user not in database.users):
                self.resource.remove(id=user.id)

    #run device check
    def checkDevice(self, database):
        print("Checking device:", self.details["name"])
        self.checkNotAdded(database)
        self.checkRemoved(database)
        print("Successfully checked:", self.details["name"])




class Database:
    def __init__(self, databaseDetails):
        self.details = databaseDetails
        self.users = self.getData()
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
    for device in devices:
        device.checkDevice(database)