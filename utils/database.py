import os

import pymysql.cursors
import re
import sqlparse

connection = None

try:
    args = {
        'host': os.getenv('DB_HOST') or "localhost",
        'port': int(os.getenv('DB_PORT') or "3306"),
        
        'user': os.getenv('DB_USER') or "root",
        'password': os.getenv("DB_PASSWORD"),
        
        'database': os.getenv('DB_NAME')
    }

    connection = pymysql.connect(**{ k: v for k,v in args.items() if v is not None or v != "" }, cursorclass=pymysql.cursors.DictCursor)
except pymysql.Error as err:
    raise Exception(err)

def extractSchema():
    if(connection):
        try:
            connection.ping(reconnect=True)
            cursor = connection.cursor()
            cursor.execute('SHOW TABLES;')
            
            tables = cursor.fetchall()

            schema = []

            for table in tables:
                table = list(table.values())[0] # Get table name
                cursor.execute('SHOW CREATE TABLE ' + table)
                result = cursor.fetchone()['Create Table']
                
                schema.append(re.sub(r" ENGINE.*", "", result))
            
            return '\n\n'.join(schema)
        except pymysql.Error as err:
            raise Exception(err)
        
def validateSQL(query):
    """
    Validate the structure of an SQL query using sqlparse.
    """
    try:
        # Parse the query, which returns a list of parsed statements.
        parsed = sqlparse.parse(query)
        if not parsed:
            return False
        
        first_token = parsed[0].tokens[0].value.upper()
        return first_token == 'SELECT'
    except Exception as e:
        return False

def sqlExecute(query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        values = cursor.fetchall()

        return values
    except pymysql.Error as err:
        print("[DEBUG] Generated SQL is failed to execute")
        raise pymysql.Error(err)