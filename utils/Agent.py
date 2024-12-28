from classes.Ollama import OllamaClient
from classes.Groq import GroqClient

from utils.prompts import CHAT_SYSTEM, SUGGESTION_QUESTIONS, FIX_SQL
from utils.database import validateSQL, sqlExecute, extractSchema
from utils.extractors import sqlExtractor

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

def chatbot():
    """
    A simple chatbot that uses the Llama model to generate SQL queries based on user input.
    """

    # Initialize the LlamaModel
    model = OllamaClient(model_name="llama3.2")

    # Initialize conversation history
    conversation_history = [
        { 'role': 'system', 'content': CHAT_SYSTEM }
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