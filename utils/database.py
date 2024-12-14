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

import re
import pymysql  # Ensure you have this imported for database operations

def extractSchema():
    if(connection):
        try:
            connection.ping(reconnect=True)
            cursor = connection.cursor()
            cursor.execute('SHOW TABLES;')

            tables = cursor.fetchall()

            result_text = ""  # This will store the final formatted text output

            for table in tables:
                table_name = list(table.values())[0]  # Get table name
                cursor.execute('SHOW CREATE TABLE ' + table_name)
                schema = cursor.fetchone()['Create Table']
                cleaned_schema = re.sub(r" ENGINE.*", "", schema)

                # Add the schema to the result text
                result_text += f"{cleaned_schema}\n\n"
            return result_text
        except pymysql.Error as err:
            raise Exception(err)