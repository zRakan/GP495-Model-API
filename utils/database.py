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
            return False, "Invalid SQL: Could not parse query."
        # Check that the query starts with a valid SQL command ( SELECT Only )
        valid_starts = {'SELECT'}
        first_token = parsed[0].tokens[0].value.upper() # parsed take first element in list, tokens is components of SQL statement ex: Select, *, From
        if first_token not in valid_starts:
            return False, f"Invalid SQL: Query must start with {', '.join(valid_starts)}."
        return True, "Valid SQL"
    
    except Exception as e:
        raise ValueError(f"SQL Validation Error: {str(e)}")