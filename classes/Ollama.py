from ollama import chat

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