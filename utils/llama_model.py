import subprocess

class LlamaModel:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate(self, prompt):
        """
        Generate a response from the Llama model using the provided prompt.
        Assumes the `ollama` CLI is installed and configured locally.
        """
        try:
            # Use the `ollama` CLI to interact with the model
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Error generating response: {result.stderr}")

            # Return the response as plain text
            return result.stdout.strip()
        except Exception as e:
            raise Exception(f"Llama model error: {str(e)}")
    def rewrite_question(self, previous_question, current_question):
        """
            Rewrite the following question to include the context of the previous question.
        """
        prompt = f"""
            Generate a rewritten question by combining the last question and the new question if they are related. If the new question is self-contained and not related to the last question, return the new question.
            Provide ONLY the rewritten question as the output, without any explanation or additional text.

        Previous Question: "{previous_question}"
        Current Question: "{current_question}"
        """
        try:
            # Use the Llama model to generate the rewritten question
            rewritten_question = self.generate(prompt)
            return rewritten_question
        except Exception as e:
            raise Exception(f"Error rewriting question: {str(e)}")