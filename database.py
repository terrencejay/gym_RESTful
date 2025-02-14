import mysql.connector
from mysql.connector import Error

host = "127.0.0.1"
user = "root"
password = "Password123!"
database = "gym"

def dbconn():
    try:
        mydb = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )
        print("connection successful")
    except mysql.connector.Error as err:
        if err.errno == 2003:
            print("Check hostname/ip,port, and, firewall")
        elif err.errno == 1045: 
            print("Error: Check username and password")
        elif err.errno == 1049:
            print("Error: check if database exists")
        else:
            print(f"Error: {err}")
        


            