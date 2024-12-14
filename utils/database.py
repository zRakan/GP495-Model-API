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

                cursor.execute('SELECT * FROM ' + table_name + ' LIMIT 3')  
                rows = cursor.fetchall()

                # Add the schema to the result text
                result_text += f"{cleaned_schema}\n\n"

                # Add the rows as a comment
                result_text += "/*\n"
                result_text += f"{len(rows)} rows from {table_name} table:\n"

                # Extract column names from the first row if rows exist
                if rows:
                    column_names = rows[0].keys()
                    result_text += "\t".join(column_names) + "\n"

                # Add the rows
                for row in rows:
                    row_values = [str(value) for value in row.values()]
                    result_text += "\t".join(row_values) + "\n"

                result_text += "*/\n\n"

            return result_text
        except pymysql.Error as err:
            raise Exception(err)