class TextPromptTemplates():

    system_prompt = '''You're a smart assistant. '''

    user_message = '''Your task is to summarize the below text.

### CONTEXT ###
```{context}```

Return the summary of the CONTEXT
'''