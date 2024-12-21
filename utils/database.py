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
def rewrite_previous_question(conversation_history):
    """
    Rewrite the previous question in the conversation history based on the current question.
    """
    if len(conversation_history) <= 2:
        raise Exception("Not enough conversation history to rewrite the previous question.")

    # Extract the previous and current questions
    previous_question = None
    current_question = None

    # Traverse the conversation history to find the last two user questions
    for message in reversed(conversation_history):
        if message['role'] == 'user':
            if current_question is None:
                current_question = message['content']
            elif previous_question is None:
                previous_question = message['content']
                break

    if not previous_question or not current_question:
        raise Exception("Could not find both previous and current questions in the conversation history.")

    # Use the LlamaModel to rewrite the previous question
    try:
        model = LlamaModel(model_name="llama3.2")
        rewritten_question = model.rewrite_question(previous_question, current_question)
        return rewritten_question
    except Exception as e:
        raise Exception(f"Error rewriting previous question: {str(e)}")

def chatbot():
    """
    A simple chatbot that uses the Llama model to generate SQL queries based on user input.
    """
    # Generate the system prompt using the database schema
    system_prompt = generate_system_prompt()

    # Initialize the LlamaModel
    model = LlamaModel(model_name="llama3.2")

    # Initialize conversation history
    conversation_history = [
        { 'role': 'system', 'content': system_prompt }
    ]

    print("Chatbot is ready! Ask your questions about the database.")
    print("Type 'exit' to quit.\n")

    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Add the user's input to the conversation history
        conversation_history.append({ 'role': 'user', 'content': user_input })

        # Rewrite the previous question only for the second question and beyond
        if len([msg for msg in conversation_history if msg['role'] == 'user']) > 1:  # Ensure at least two user questions
            try:
                # Rewrite the previous question based on the current question
                rewritten_question = rewrite_previous_question(conversation_history)
                print(f"Rewritten Previous Question: {rewritten_question}")
            except Exception as e:
                print(f"Error rewriting previous question: {str(e)}")

        # Prepare the prompt for the Llama model
        # Combine the conversation history into a single prompt
        prompt = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])

        try:
            # Generate a response using the Llama model
            response = model.generate(prompt)

            # Add the chatbot's response to the conversation history
            conversation_history.append({ 'role': 'assistant', 'content': response })

            # Print the chatbot's response
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")

# Run the chatbot
if __name__ == "__main__":
    chatbot()