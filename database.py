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
    insert = 0
    test = 1
    
    if insert == 1:
        cursor = connection.cursor()
        """variabele insert"""
        add_action = ("INSERT INTO History "
                      "(Status, Waterstand, Windkracht, Windrichting, Instantie) "
                      "VALUES (%(status)s, %(waterstand)s, %(windkracht)s, %(windrichting)s, %(instantie)s)")

        data_action = {
            'status': 1,
            'waterstand': 75,
            'windkracht': 9,
            'windrichting': 359,
            'instantie': "Primair"
        }

        cursor.execute(add_action, data_action) #combineer de data met de query

        connection.commit() #Voer de query uit

    """Einde insert"""
    """Start test"""
    if test == 1:
        cursor = connection.cursor()
        row = cursor.fetchone()
        query = ("SELECT * FROM History")
        cursor.execute(query)

        for row in cursor:
            print(row)
        """Einde test"""
    cursor.close()
    connection.close()




    cursor.close()
    connection.close()
