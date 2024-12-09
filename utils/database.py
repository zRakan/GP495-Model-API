import pymysql.cursors
import re

connection = None

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        database='hospital',
        cursorclass=pymysql.cursors.DictCursor
    )
except pymysql.Error as err:
    raise Exception(err)

def extractSchema():
    if(connection):
        try:
            connection.ping(reconnect=True)
            cursor = connection.cursor()
            cursor.execute('SHOW TABLES;')
            
            tables = cursor.fetchall()

            result = []

            for table in tables:
                table_name = list(table.values())[0] # Get table name
                cursor.execute('SHOW CREATE TABLE ' + table_name)
                schema = cursor.fetchone()['Create Table']
                cleaned_schema = (re.sub(r" ENGINE.*", "", schema))

                cursor.execute('SELECT * FROM '+ table_name +' LIMIT 3')  
                rows = cursor.fetchall()

                result.append({  
                    "table_name": table_name,  
                    "schema": cleaned_schema,  
                    "rows": rows  
                }) 

            return result
        except pymysql.Error as err:
            raise Exception(err)