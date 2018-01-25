import mysql.connector
from mysql.connector import errorcode

"""Connection with database (doesnt change beceause of static ip)"""
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


def insertIntoDatabase(dataStatus, dataWeerstand, dataWindkracht, dataWindrichting, dataInstatie):
    """Prepared query"""
    add_action = ("INSERT INTO History "
                  "(Status, Waterstand, Windkracht, Windrichting, Instantie) "
                  "VALUES (%(status)s, %(waterstand)s, %(windkracht)s, %(windrichting)s, %(instantie)s)")

    """Bind varbiales into query"""
    data_action = {
        'status': dataStatus,
        'waterstand': dataWeerstand,
        'windkracht': dataWindkracht,
        'windrichting': dataWindrichting,
        'instantie': dataInstatie
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

"""Closes the connection the the database."""
def closeDatabaseConnection():
    cursor.close()  # Shut down the cursor
    connection.close()  # Shut down the connection
    success = print("Connection closed.")
    return success



#  test data 1, 75, 9, 359, 'Primair'
"""Executes the function with given data. !position == variable!"""
insertIntoDatabase(1, 25, 3, 456, 'Primair')
closeDatabaseConnection()
