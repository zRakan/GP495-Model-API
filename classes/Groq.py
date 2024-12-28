import os
from groq import Groq

from utils.prompts import REWRITE_QUESTION

class GroqClient:
    _instance = None

    def __new__(cls, model_name):
        if not cls._instance:
            cls._instance = super(GroqClient, cls).__new__(cls)
            cls._instance.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            cls._instance.model_name = model_name

        return cls._instance

    def generate(self, messages):
        """
        Generate a response from the Groq inference using the provided prompt.
        """

        try:
            # Clean conversation from non-text messages
            cleanedMessages = [message for message in messages if 'type' not in message]

            response = self.client.chat.completions.create(model=self.model_name, messages=cleanedMessages)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq inference error: {str(e)}")
        
    def rewrite_question(self, previous_question, current_question):
        """
            Rewrite the following question to include the context of the previous question.
        """

        prompt = [
            { 'role': 'system', 'content': REWRITE_QUESTION },

            {
                'role': 'user',
                'content': f'''Previous Question: "{previous_question}"
Current Question: "{current_question}"'''
            }
        ]
        
        try:
            # Use the Ollama to generate the rewritten question
            rewritten_question = self.generate(prompt)
            return rewritten_question
        except Exception as e:
            raise Exception(f"Error rewriting question: {str(e)}")