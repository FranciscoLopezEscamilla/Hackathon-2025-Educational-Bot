class TextPromptTemplates:

    system_prompt = '''You're a smart assistant that are excellent on following instructions.'''

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
4. Split your summary into the following sections: overview, important_concepts, features, relevance, conclusion.
5. Add the necessary information to fill up the sections.

Return a string with a valid json format. 
Use these sections as key names.
Do not include the word 'json' as part of your respond.
'''

    description_prompt = '''You will receive an input text in json format, identify the keys and values.
Your task is to rephrase all values into a short sentence.

Generate new phrases like describing to dalle model how to draw a picture. 
Be as descriptive and detailed as you can. 
The new phrases will be used for dalle llm to generate an image based on the text you provide.

The images will be used for learning purposes, keep that in mind when generating the sentences.
Return one new sentece per value you find in the text.

#### INPUT TEXT ###
{text}

### EXAMPLES ###

text: The article highlights how Python programming serves as a modern alternative to traditional art forms through the creation of generative art focusing on the principles processes and tools essential for art generation using coding and artificial intelligence
new phrase: the python programming logo simulating its creating new art using generative AI holding a painting tool.


Return a string with a valid json format.
Do not include the word 'json' as part of your respond.
'''
