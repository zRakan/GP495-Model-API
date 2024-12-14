import pymysql.cursors
import re
import sqlparse
from utils.llama_model import LlamaModel

connection = None

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        database='DATABASE',
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

def generate_questions(schema):
    """
    Generate 4 SQL questions based on the database schema using the Llama model.
    """
    if not schema:
        raise Exception("Schema is empty. Cannot generate questions.")

    # Format the schema into a single string
    schema_text = "\n\n".join(schema)

    # Define the prompt
    prompt = f"""You are an expert SQL assistant. Based on the following database schema, generate 4 meaningful SQL questions that a user might ask. 
    The questions should be related to retrieving data, aggregating information, or analyzing relationships between tables, short question.

    Schema:{schema_text}

    Provide only the questions and with numbered list.
    """

    try:
        model = LlamaModel(model_name="llama3.2")
        response = model.generate(prompt)
        questions = response.split("\n")
        return [q.strip() for q in questions if q.strip()]

    except Exception as e:
        raise Exception(f"Llama model error: {str(e)}")