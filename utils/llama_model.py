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