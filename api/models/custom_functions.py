class CustomFunctions:

    functions = [
    {
        "type":"function",
        "function" :{
            "name": "summarize_text",
            "description" : "summarize text into sections",
            "strict": True,
            "parameters":{
                "type": "object",
                "properties":{
                    "summary":{
                        "type": "string",
                        "description": "Summary of the text divided into sections"
                    }
                },
                "required":["summary"],
                "additionalProperties": False
            }    
        }
    }
    ]