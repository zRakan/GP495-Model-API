from ollama import chat

from utils.prompts import REWRITE_QUESTION

class OllamaClient:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate(self, messages):
        """
        Generate a response from the Ollama model using the provided prompt.
        """

        try:
            # Clean conversation from non-text messages
            cleanedMessages = [message for message in messages if 'type' not in message]

            response = chat(model=self.model_name, messages=cleanedMessages)
            return response.message.content
        except Exception as e:
            raise Exception(f"OLlama model error: {str(e)}")
        
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