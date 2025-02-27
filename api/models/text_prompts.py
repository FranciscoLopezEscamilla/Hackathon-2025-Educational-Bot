class TextPromptTemplates:

    system_prompt = '''You're a smart assistant that helps users to learn and get information of certain topics.'''

    summarization_text_prompt = '''You're going to receive two inputs, a context and a user query.
Please read and understand the context below delimited by triple backticks and the user query and follow the next instructions.

### CONTEXT ###
```{context}```

### QUERY ###
```{query}```

Follow this instructions:
### INSTRUCTIONS ###
1. Read carefully and understand the context
2. Create a summary of the context. The summary must have the most important elements on the text.
3. Make sure that the summary contains the necessary information that the user is looking for in the query.
4. Split your summary into sections and short paragraphs.

Return a string with a valid json format. Use the sections as key names. Do not include the word 'json' as part of your respond.
'''

    description_prompt = ""