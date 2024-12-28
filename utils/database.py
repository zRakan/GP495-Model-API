import pymysql.cursors
import re
import sqlparse

connection = None

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
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

            schema = []

            for table in tables:
                table = list(table.values())[0] # Get table name
                cursor.execute('SHOW CREATE TABLE ' + table)
                result = cursor.fetchone()['Create Table']
                
                schema.append(re.sub(r" ENGINE.*", "", result))
            
            return schema
        except pymysql.Error as err:
            raise Exception(err)
        
def validate_sql(query):
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
        raise pymysql.Error(err)