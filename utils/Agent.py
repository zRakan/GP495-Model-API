from classes.Ollama import OllamaClient
from classes.Groq import GroqClient

from utils.prompts import CHAT_SYSTEM, SUGGESTION_QUESTIONS, FIX_SQL, PLOTLY_DATAPOINTS
from utils.database import validateSQL, sqlExecute, extractSchema
from utils.extractors import sqlExtractor, jsonExtractor

import pandas as pd
from pymysql import Error as sqlError

def generateQuestions(schema):
    """
    Generate 4 SQL questions based on the database schema using the Llama model.
    """
    if not schema:
        raise Exception("Schema is empty. Cannot generate questions.")

    # Format the schema into a single string
    schema_text = "\n\n".join(schema)

    # Define the prompt
    prompt = SUGGESTION_QUESTIONS.format(schemaText=schema_text)

    try:
        model = GroqClient(model_name="llama-3.1-8b-instant")
        response = model.generate([{ 'role': 'user', 'content': prompt }])
        
        questions = response.split("\n")
        questions = [q.strip() for q in questions if q.strip()]

        return questions[(1 if len(questions) > 4 else 0):]

    except Exception as e:
        raise Exception(f"Llama model error: {str(e)}")
    
def rewriteQuestion(previous, current):
    """
    Rewrite the previous question in the conversation history based on the current question.
    """

    # Use the LlamaModel to rewrite the previous question
    try:
        model = GroqClient(model_name="llama-3.1-8b-instant")

        rewritten_question = model.rewrite_question(previous, current)
        return rewritten_question
    except Exception as e:
        raise Exception(f"Error rewriting previous question: {str(e)}")

def sqlSafeExecute(input, query, schema):
    try:
        if(not validateSQL(query)):
            raise sqlError('Not `SELECT` SQL')

        result = sqlExecute(query)
        return result, query
    except sqlError as err:
        model = GroqClient(model_name="llama-3.1-8b-instant")
        
        newQuery = model.generate([
            { 'role': 'system', 'content': FIX_SQL.format(input=input, err=err, query=query, schema_data=schema) }
        ])

        # Extract SQL from LLM response
        newQuery = sqlExtractor(newQuery)

        # Call the function again
        return sqlSafeExecute(input, newQuery, schema)

from string import Template
def generatePlotly(df, query):
    try:
        model = GroqClient(model_name="llama-3.1-8b-instant")
        
        plotlyJSON = model.generate([
            { 'role': 'system', 'content': Template(PLOTLY_DATAPOINTS).substitute(df=df) }
        ])

        return jsonExtractor(plotlyJSON)
    except Exception as err:
        print(err)
        return None

def sendPrompt(conversation, prompt):
    try:
        sqlSchema = extractSchema()

        model = GroqClient(model_name="llama-3.1-8b-instant")
        print(f"""Convo: {len(conversation)}""")

        # Initial interaction
        if(len(conversation) == 0):
            conversation.append({ 'role': 'system', 'content': CHAT_SYSTEM.format(schemaData=sqlSchema, RAG="") })

        # Re-writing user's message (if applicable)
        if(len(conversation) > 2):
            previousPrompt = None
            
            for message in reversed(conversation):
                if('type' in message): continue # Ignore non-text messages

                if(message['role'] == 'user'):
                    previousPrompt = message['content']
                    break

            if(previousPrompt is not None):
                prompt = rewriteQuestion(previousPrompt, prompt)

        # Send user's message
        conversation.append({ 'role': 'user', 'content': prompt })
        response = model.generate(conversation)

        # Check for SQL
        sqlResult, sqlQuery = sqlSafeExecute(prompt, response, sqlSchema)

        # Add LLM resposne to the conversation
        conversation.append({ 'role': 'assistant', 'content': sqlQuery })

        # Generate Markdown
        sqlMarkdown = pd.DataFrame(sqlResult).to_markdown()
        conversation.append({ 'type': 'Markdown', 'role': 'assistant', 'content': sqlMarkdown })

        # Generate Plotly
        sqlPlotly = generatePlotly(sqlMarkdown, prompt)

        for plot in sqlPlotly:
            conversation.append({ 'type': 'Plotly', 'role': 'assistant', 'content': plot })

        return { 'conversation': conversation }
    except Exception as e:
        raise Exception(e)