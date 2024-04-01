import json
import replicate

from tinytune.util.prompt import ValidatePrompt
from tinytune.llmcontext import LLMContext, Model, Message
from typing import Callable, Any

class ReplicateMessage(Message):
    __slots__ = ("Role", "Content")

    def __init__(self, role: str, content: str):
        super().__init__(role, content)

    def __str__(self) -> str:
        if (self.Role == "user"):
            return f"[INST] {self.Content} [/INST]"
        return self.Content
            
class ReplicateContext(LLMContext[ReplicateMessage]):
    def __init__(self, model: Model, apiKey: str, promptFile: str | None = None):
        super().__init__(model)

        self.APIKey: str = apiKey
        self.Messages: list[ReplicateMessage] = []
        self.QueuePointer: int = 0
        self.Model = replicate.models.get(f"{model.Owner}/{model.Name}")

    def LoadMessages(self, promptFile: str = "prompts.json") -> None:
        self.PromptFile = promptFile
 
        with open(promptFile, "r") as fp:
            self.Messages = json.load(fp)

    def Save(self, promptFile: str = "prompts.json") -> Any: 
        try:
            with open(promptFile, "w") as fp:
                fp.write("\n".join([str(message) for message in self.Messages])) 
                
        except:
            print("An error occured in saving messages.")
            return self 

        return self
    
    def Prompt(self, message: ReplicateMessage):
        self.MessageQueue.append(message)

        return self

    def Run(self, *args, **kwargs):
        stream: bool | None = kwargs.get("stream")
        
        if (stream == None):    
            stream = False 

        while (self.QueuePointer < len(self.MessageQueue)):
            self.Messages.append(self.MessageQueue[self.QueuePointer])

            response = replicate.stream(self.Model, input = {
                    "prompt": " ".join([str(message) for message in self.Messages])
                }) 
            
            self.Messages.append(ReplicateMessage("assistant", ""))    
        
            if (stream):
                for chunk in response:
                    content = chunk.data

                    if (content != None):
                        self.Messages[len(self.Messages) - 1].Content += content 
                    
                    self.OnGenerateCallback(content)
                
            self.QueuePointer += 1

        return self