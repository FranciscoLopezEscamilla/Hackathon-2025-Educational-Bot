import os
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

class AssistantService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_KEY'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_version=os.getenv('AZURE_OPENAI_VERSION'),
        )
        self.assistant = self.create_assistant()

    def create_assistant(self):
        """Creates and returns an AI assistant instance."""
        return self.client.beta.assistants.create(
            name="FAQ bot Assistant",
            instructions="You are an AI assistant that can write code to help answer math questions.",
            model="gpt-4"  # Update this to match your model's deployment name
        )

    def create_thread(self):
        """Creates a new chat thread."""
        return self.client.beta.threads.create()

    def send_message(self, thread_id: str, user_message: str):
        """Adds a user message to the thread."""
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

    def run_thread(self, thread_id: str):
        """Runs the assistant thread and waits for completion."""
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id,
            max_prompt_tokens=500,
            max_completion_tokens=500
        )

        # Wait for completion
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(5)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

        return run

    def get_thread_messages(self, thread_id: str):
        """Fetches the messages from a thread."""
        return self.client.beta.threads.messages.list(thread_id=thread_id)

