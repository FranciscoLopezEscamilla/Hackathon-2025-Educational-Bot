import os
import time
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key='8ZsRwd1sNLDi2hOJwp88Sm71BwNRukD1n9nj3vZKOisjImedxuBbJQQJ99BCACHYHv6XJ3w3AAAAACOG6f3u',
    azure_endpoint='https://gonpr-m7rslzjz-eastus2.openai.azure.com/',
    api_version="2024-08-01-preview",
)

# Create an assistant
assistant = client.beta.assistants.create(
    name="Math Assist",
    instructions="You are an AI assistant that can write code to help answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4" # You must replace this value with the deployment name for your model.
)

print(assistant)

# Create a thread
thread = client.beta.threads.create()

print(thread)

# Add a user question to the thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation 3x + 11 = 14. Can you help me?"
)

print(message)

# Run the thread and poll for the result
# run = client.beta.threads.runs.create_and_poll(
#     thread_id=thread.id,
#     assistant_id=assistant.id,
#     instructions="Please address the user as Jane Doe. The user has a premium account.",
# )

# Run the thread

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
  )

# Looping until the run completes or fails

while run.status in ['queued', 'in_progress', 'cancelling']:

  time.sleep(1)

  run = client.beta.threads.runs.retrieve(

    thread_id=thread.id,

    run_id=run.id

  )


if run.status == 'completed':

  messages = client.beta.threads.messages.list(

    thread_id=thread.id

  )

  print(messages)

elif run.status == 'requires_action':

  # the assistant requires calling some functions

  # and submit the tool outputs back to the run

  pass

else:

  print(run.status)



# print("Run completed with status: " + run.status)

# if run.status == "completed":
#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#     print(messages.to_json(indent=2))