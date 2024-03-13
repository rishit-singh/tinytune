from typing import Callable, Any
from dataclasses import dataclass
import json

class Message:
    __slots__ = ("Role", "Content")

    def __init__(self, role: str, content: str):
        self.Role = role
        self.Content = content

    def ToDict(self):
        return {
            "role": self.Role,
            "content": self.Content
        }
     
class Model:
    def __init__(self, owner: str, name: str):
        self.Owner: str = owner
        self.Name: str = name
        
class LLMContext[MessageType]:
    def __init__(self, model: Model):
        self.Messages: list[MessageType] = [] 
        self.MessageQueue: list[MessageType] = []
        self.Model: Model = model
        self.OnGenerateCallback: Callable[[list[str]], None] = lambda tokens : None 

    def Top(self) -> MessageType:
        return self.Messages[len(self.Messages) - 1]

    def Prompt(self, message: MessageType) -> Any:
        self.MessageQueue.append(message)
        return self

    def Save(self, promptFile: str = "prompts.json") -> Any: 
        try:
            with open(promptFile, "w") as fp:
                json.dump([ message.ToDict() for message in self.Messages ], fp, indent=2)
                
        except Exception as e:
            print(f"An error occured in saving messages: {e.args[0]}")
            return self 

        return self

    def Run(self, *args, **kwargs):   
        pass
        return self

