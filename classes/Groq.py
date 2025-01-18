import os
from groq import Groq

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