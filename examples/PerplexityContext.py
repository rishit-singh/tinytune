import sys

sys.path.append("../")

import json
from tinytune.util.prompt import ValidatePrompt
from tinytune.llmcontext import LLMContext, Model
from typing import Callable, Any
import openai

class PerplexityMessage:
    __slots__ = ("Role", "Content")

    def __init__(self, role: str, content: str):
        self.Role = role
        self.Content = content
    
    def ToDict(self):
        return {
            "role": self.Role,
            "content": (self.Content)
        } 

class PerplexityContext(LLMContext[PerplexityMessage]):
    def __init__(self, model: str, apiKey: str, promptFile: str = None):
        super().__init__(Model("mistralai", model))
        self.APIKey: str = apiKey
        self.Messages: list[PerplexityMessage] = []
        self.QueuePointer: int = 0
        self.LLM = openai.OpenAI(api_key=self.APIKey, base_url="https://api.perplexity.ai")

    def LoadMessages(self, promptFile: str = "prompts.json"):
        self.PromptFile = promptFile

        with open(promptFile, "r") as fp:
            self.Messages = json.load(fp)

    def Save(self, promptFile: str = "prompts.json"): 
        try:
            with open(promptFile, "w") as fp:
                json.dump([ message.ToDict() for message in self.Messages ], fp, indent=2)
                
        except:
            print("An error occured in saving messages.")
            return self 

        return self
    
    def AddPrompt(self, prompt: dict, onError: Callable[[KeyError], Any] = None) -> bool:
        try:
            ValidatePrompt(prompt)
            self.Messages.append(prompt)

        except KeyError as e:
            if (onError == None):
                raise e
            onError(e)

            return False

        return True
    
    def Prompt(self, message: PerplexityMessage):
        self.MessageQueue.append(message)

        return self

    def Run(self, stream: bool = False):
        while (self.QueuePointer < len(self.MessageQueue)):
            self.Messages.append(self.MessageQueue[self.QueuePointer])

            response = self.LLM.chat.completions.create(model=self.Model.Name, 
                                           messages=[ message.ToDict() for message in self.Messages ],
                                           temperature=0,
                                           stream=stream)
          
            self.Messages.append(PerplexityMessage("assistant", ""))    

            if (stream):
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if (content != None):
                        self.Messages[len(self.Messages) - 1].Content += content 
                    # print(chunk)
                    self.OnGenerateCallback(content)

            self.QueuePointer += 1

        return self