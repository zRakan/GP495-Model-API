import pymysql.cursors
import re
from uuid import uuid4
from qdrant_client import QdrantClient
from ollama import chat
import pandas as pd
import re
import os
from groq import Groq

clientgroq = Groq(
    api_key="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"
)

# add to req file pip install qdrant-client[fastembed] uuid 

client = QdrantClient(host='localhost', port=6333)

COLLECTION = "Queries_SQL"

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

def generate_system_prompt(RAG):
    """
    Generates a system prompt for an AI assistant to create SQL queries based on a database schema.
    """
    # Extract the schema data
    schema_data = extractSchema()

    # Define the system prompt
    system_prompt = f"""You are a MySQL expert. Please help to generate an SQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines.

# Tables: 
{schema_data}


# similar question with query
-this is a similar question with it confirmed SQL query use it to generate a query to meet the user's question
{RAG}

# Response Guidelines:
- Do not generate queries that modify the database, such as `UPDATE`, `DELETE`, `INSERT`, or `DROP`.
- Use the schema to answer user's question and understand the structure of the database and generate accurate queries.
- Do not make assumptions about data or generate queries for tables or columns that are not explicitly defined in the schema.
- Only provide the SQL code, without any explaination
- Don't answer any question that not related to the schema context
- Don't write ```sql at the start of the code and don't put``` at the end just write code start with 'SELECT ....'
"""

    return system_prompt

# Main chatbot function
def chatbot():
    """
    A simple chatbot that uses the Llama model to generate SQL queries based on user input.
    """

    print("Chatbot is ready! Ask your questions about the database.")
    print("Type 'exit' to quit.\n")

    user_input = input("You: ")
    rag = getRAG(user_input)
    system_prompt = generate_system_prompt(rag)

    # Initialize conversation history
    conversation_history = [
        { 'role': 'system', 'content': system_prompt }
    ]
    # Add the user's input to the conversation history
    conversation_history.append({ 'role': 'user', 'content': user_input })

    # Send the conversation history to the chat model
    response =  clientgroq.chat.completions.create(model='llama-3.1-8b-instant', messages=conversation_history)

    # Add the chatbot's response to the conversation history
    conversation_history.append({ 'role': 'assistant', 'content': response.choices[0].message.content })

    # Print the chatbot's response
    print(response.choices[0].message.content)

    conversation_history = [
        { 'role': 'system', 'content': system_prompt }
    ]
    sqlStatement = response.choices[0].message.content
    SQLOutput = SQLCall(user_input , sqlStatement)
    print(SQLOutput)
    code = generatePlotlyJSCode(SQLOutput , user_input)
    print(code)
    print(f"""waht rakan wants
        the SQL from the LLM {sqlStatement}
        the MD DF {SQLOutput}
        the json {code}
          """ )
    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        # Add the user's input to the conversation history
        conversation_history.append({ 'role': 'user', 'content': user_input })

        # Send the conversation history to the chat model
        response = clientgroq.chat.completions.create(model='llama-3.1-8b-instant', messages=conversation_history)
        sqlCode = response.choices[0].message.content
        # Add the chatbot's response to the conversation history
        conversation_history.append({ 'role': 'assistant', 'content': sqlCode })

        # Print the chatbot's response
        print(f"the model res :{sqlCode} \n\n")
        df = SQLCall(user_input  , sqlCode)
        print(f"the SQL output {df}\n\n ")
        print(f"the plotly fig code : {generatePlotlyJSCode(df, user_input )}")


def errorSystemPrompt(err , input , query):
    prompt = '''
            You are a MySQL expert. Please help to Fix this given SQL query to answer the question given by the User. Your response should ONLY be based on the given context and follow the response guidelines.   
# User question:
{input}

# Error by mysql:
{err}

# Old generated query:
-This query have an issue or issues
{query}

# Tables: 
{schema_data}

# Response Guidelines:
- Do not generate queries that modify the database, such as `UPDATE`, `DELETE`, `INSERT`, or `DROP`.
- Use the schema to answer user's question and understand the structure of the database and generate accurate queries.
- Do not make assumptions about data or generate queries for tables or columns that are not explicitly defined in the schema.
- Only provide the SQL code, without any explaination
- Don't answer any question that not related to the schema context
- If the user question may have mutiple queries write it as one query user "union" or what you need
'''

    return prompt


def SQLCall(input , query ):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        values = cursor.fetchall()
        df = pd.DataFrame(values)
        return df.to_markdown()
    except pymysql.Error as err:
            # raise Exception(err)
            errorHandler = [
                 { 'role': 'system', 'content': errorSystemPrompt(err, input , query)},
            ]
            response = clientgroq.chat.completions.create(model='llama-3.1-8b-instant', messages=errorHandler)
            # we may add this to the history or not waiting for the leader
            SQLCall( input ,response.choices[0].message.content)


def addValue(bool , input , query):
    if bool:
        unique_id = str(uuid4())
        
        client.add(collection_name=COLLECTION, documents=[input], metadata=[ {"SQL" : query } ], ids=unique_id)

def getRAG(input):
    search_result = client.query(
        collection_name=COLLECTION,
        query_text=input,
        limit= 1
    )
    return(f'the qusetion: {search_result[0].metadata.get("document")} the SQL: {search_result[0].metadata.get("SQL")}')



def generatePlotlyJSCode( df, question):
    f = 'second output for bar plot : {"data":[{"x":["A","B","C","D"],"y":[10,20,30,40],"type":"bar","marker":{"color":"orange"} }],"layout":{"title":"Bar Plot Example","xaxis":{"title":"Categories"},"yaxis":{"title":"Values"} } }'
    s = 'first output for scatter plot : {"data":[{"x":[1,2,3,4,5],"y":[2,4,6,8,10],"type":"scatter","mode":"lines","line":{"color":"blue"} }],"layout":{"title":"Line Plot Example","xaxis":{"title":"X-axis"},"yaxis":{"title":"Y-axis"} } }'
    t = 'third output for pie plot : {"data":[{"labels":["Apple","Banana","Cherry","Date"],"values":[30,20,40,10],"type":"pie"}],"layout":{"title":"Pie Chart Example"} }'  
    system_msg = f'''The following is a pandas DataFrame that contains the results of the query that answers the question the user asked: {question}
The following is information about the resulting pandas DataFrame 'df': {df}

**Take this examples for the output depending on the user question and choose the best one:**
- Examples of output:
 - * {f}
 - * {s}
 - * {t}

**Use the data of the dataframe to fill the output with values from the dataframe**
- Only provide a JSON code for Plotly.js,
- I will use your output it for `JSON.parse` *MAKE SURE* the output is *correct* JSON.
'''
    
    plot_generation = [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': "Use this dataframe {df}."}
    ]

                        
    response = clientgroq.chat.completions.create(model='llama-3.1-8b-instant', messages=plot_generation)
    cleanCode = response.choices[0].message.content

    return sanitize_plotly_code(extract_javascript_code(cleanCode))


def sanitize_plotly_code(plotly_code):
    plotly_code = plotly_code.replace("Plotly.newPlot('myDiv', data);", "").strip()
    return plotly_code


def extract_javascript_code(markdown_string):
    pattern = r"```[\w\s]*javascript\n([\s\S]*?)```|```([\s\S]*?)```"
    matches = re.findall(pattern, markdown_string, re.IGNORECASE)

    javascript_code = []
    for match in matches:
        javascript = match[0] if match[0] else match[1]
        javascript_code.append(javascript.strip())

    if len(javascript_code) == 0:
        return markdown_string
    
    return javascript_code[0]


if __name__ == "__main__":
    chatbot()