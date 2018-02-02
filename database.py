import mysql.connector
from mysql.connector import errorcode

beginDatum = "2017-01-30 09:50:42"
eindDatum = "2019-01-30 09:51:12"

"""Connection with database (doesnt change beceause of static ip)"""


def makeDatabaseConnection():
    global connection
    global cursor
    connection = mysql.connector.connect(host='192.168.42.2',
                                         user="root",
                                         passwd="root",
                                         database='maeslantkering', )
    cursor = connection.cursor(buffered=True, dictionary=True)
    """try to get 1 result back (not all because of possible giant query)"""
    try:
        cursor.execute("SELECT * FROM History LIMIT 1")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:  # no access to server
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:  # database error
            print("Database does not exist")
        else:
            print(err)  # get other errors


"""Insert query function"""


def insertIntoDatabase(dataStatus, dataWaterstand, dataWindkracht, dataWindrichting, dataInstatie, dataNeerstlag):
    """Prepared query"""
    add_action = ("INSERT INTO History "
                  "(Status, Waterstand, Windkracht, Windrichting, Instantie, Neerslag) "
                  "VALUES (%(status)s, %(waterstand)s, %(windkracht)s, %(windrichting)s, %(instantie)s, %(neerslag)s)")

    """Bind varbiales into query"""
    data_action = {
        'status': dataStatus,
        'waterstand': dataWaterstand,
        'windkracht': dataWindkracht,
        'windrichting': dataWindrichting,
        'instantie': dataInstatie,
        'neerslag': dataNeerstlag
    }
    """Check if query is well executed else catch errors and return them."""
    try:
        cursor.execute(add_action, data_action)  # Insert the values from the data into the main query
        connection.commit()  # Execute the query
    except TypeError as e:
        status = print(e)
    else:
        status = print("Insert succesful.")
    return status

    """Krijg gebeurtenis geschiedenis"""


def getHistoryData(dataTuple):
    """Prepared query"""
    dataBeginTijd,dataEindTijd = dataTuple
    add_action = (
        "SELECT DATE_FORMAT(Tijd, '%d-%m-%Y %H:%i') AS Tijd ,Status, Waterstand, Windkracht, Windrichting, Instantie, Neerslag FROM History "
        "WHERE Tijd BETWEEN (%(beginTijd)s) AND (%(eindTijd)s) ORDER BY Tijd DESC")

    """Bind varbiales into query"""
    data_action = {
        'beginTijd': dataBeginTijd,
        'eindTijd': dataEindTijd
    }

    """Check if query is well executed else catch errors and return them."""
    try:
        cursor.execute(add_action, data_action)  # Insert the values from the data into the main query
        rows = cursor.fetchall()
    except TypeError as e:
        status = print(e)
    else:
        status = rows
    return status

def getHistory(dataTuple):
    makeDatabaseConnection()
    data = getHistoryData(dataTuple)
    closeDatabaseConnection()
    return data

"""Closes the connection the the database."""


def closeDatabaseConnection():
    cursor.close()  # Shut down the cursor
    connection.close()  # Shut down the connection
    success = print("Connection closed.")
    return success

#
# def getDateValues(status):
#     for row in status:
#         for key in row:
#             print(row[key], end=" ")
#         print(row)
#     return


#makeDatabaseConnection()
#print(getHistoryData(dataTuple)
#closeDatabaseConnection()
