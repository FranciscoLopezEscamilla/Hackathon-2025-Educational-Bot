class TextPromptTemplates():

    system_prompt = "You're a smart assistant"

    user_message = '''Your task is to understand the CONTEXT below delimited by triple backticks and follow the next instructions.
### CONTEXT ###
```{context}```

### INSTRUCTIONS ###

1. Understand the text
2. Make a summary of the text
3. Based on the summary, try to generate a description for an image that summarizes the text, be concise.
4. Return only the description of the image
'''