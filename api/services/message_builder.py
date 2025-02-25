class MessageBuilder:
    def __init__(self, system_message: str):
        self.messages = [{"role": "system", "content": system_message}]
        
    def append_messages(self, role, content, index: int = 1):
        self.messages.insert(index, {"role": role, "content": content})