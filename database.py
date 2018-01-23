import mysql.connector
from mysql.connector import errorcode


try:
    connection = mysql.connector.connect(host='192.168.42.2',
                                  user="root",
                                  passwd="root",
                                  database='maeslantkering')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:

    cursor = connection.cursor()
    row = cursor.fetchone()
    query = ("SELECT * FROM History")
    cursor.execute(query)

    for row in cursor:
        print(row)

    print("gelukt?")
    cursor.close()
    connection.close()
