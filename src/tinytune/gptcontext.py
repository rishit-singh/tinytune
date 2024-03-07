import openai
import json
from tinytune.util.prompt import ValidatePrompt
from tinytune.llmcontext import LLMContext, Model
from typing import Callable, Any

class GPTMessage:
    __slots__ = ("Role", "Content")

    def __init__(self, role: str, content: str):
        self.Role = role
        self.Content = content
    
    def ToDict(self):
        return {
            "role": self.Role,
            "content": self.Content
        } 

class GPTContext(LLMContext[GPTMessage]):
    def __init__(self, model: str, apiKey: str, promptFile: str = None):
        super().__init__(Model("openai", model))

        self.APIKey: str = apiKey
        self.Messages: list[GPTMessage] = []
        self.QueuePointer: int = 0

        openai.api_key = self.APIKey

    def LoadMessages(self, promptFile: str = "prompts.json"):
        self.PromptFile = promptFile

        with open(promptFile, "r") as fp:
            self.Messages = json.load(fp)

    def Save(self, promptFile: str = "prompts.json") -> bool: 
        try:
            with open(promptFile, "w") as fp:
                json.dump(self.Messages, fp, indent=2)
                
        except:
            print("An error occured in saving messages.")
            return False

        return True
    
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

    def Send(self, _messages: list[dict[str, str]]) -> dict:
        print(f"Message size: {len(self.Messages)}")
        print(_messages)

        if (len(self.Messages) < 1):
            for message in _messages:
                self.Messages.append(message)

        return dict(openai.ChatCompletion.create(model=self.Model, messages=_messages)["choices"][0]["message"])

    def Prompt(self, message: GPTMessage):
        self.MessageQueue.append(message)

        return self

    def Run(self, stream: bool = False):
        while (self.QueuePointer < len(self.MessageQueue)):
            self.Messages.append(self.MessageQueue[self.QueuePointer])

            response = openai.chat.completions.create(model=self.Model.Name, 
                                           messages=[ message.ToDict() for message in self.Messages ] + [self.MessageQueue[self.QueuePointer].ToDict()],
                                           temperature=0,
                                           stream=stream)
            

            self.Messages.append(GPTMessage("assistant", ""))    
        
            if (stream):
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if (content != None):
                        self.Messages[len(self.Messages) - 1].Content += content 
                    # print(chunk)
                    self.OnGenerateCallback(content)
                
            
            self.QueuePointer += 1

        return self