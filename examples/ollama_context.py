import openai
import json
from tinytune.util.prompt import ValidatePrompt
from tinytune.llmcontext import LLMContext, Model, Message
from typing import Callable, Any


class OllamaMessage(Message):
    __slots__ = ("Role", "Content")

    def __init__(self, role: str, content: str):
        super().__init__(role, content)


class OllamaContext(LLMContext[OllamaMessage]):
    def __init__(
        self,
        baseUrl: str,
        model: str,
        apiKey: str = "ollama",
        promptFile: str | None = None,
    ):
        super().__init__(Model("openai", model))

        self.Messages: list[OllamaMessage] = []
        self.QueuePointer: int = 0
        self.Client = openai.OpenAI(base_url=baseUrl, api_key=apiKey)

    def LoadMessages(self, promptFile: str = "prompts.json") -> None:
        self.PromptFile = promptFile

        with open(promptFile, "r") as fp:
            self.Messages = json.load(fp)

    def Save(self, promptFile: str = "prompts.json") -> Any:
        try:
            with open(promptFile, "w") as fp:
                json.dump([message.ToDict() for message in self.Messages], fp, indent=2)

        except:
            print("An error occured in saving messages.")
            return self

        return self

    def Prompt(self, message: OllamaMessage):
        self.MessageQueue.append(message)

        return self

    def Run(self, *args, **kwargs):
        stream: bool | None = kwargs.get("stream")

        while self.QueuePointer < len(self.MessageQueue):
            self.Messages.append(self.MessageQueue[self.QueuePointer])

            response = self.Client.chat.completions.create(
                model=self.Model.Name,
                messages=[message.ToDict() for message in self.Messages]
                + [self.MessageQueue[self.QueuePointer].ToDict()],
                temperature=0,
                stream=stream,
            )

            if stream:
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content != None:
                        self.Messages[len(self.Messages) - 1].Content += content

                    self.OnGenerate(content)
            else:
                self.Messages[-1] = OllamaMessage(
                    "user", str(response.choices[0].message.content)
                )

            self.QueuePointer += 1

        return self


class O1Context(LLMContext[OllamaMessage]):
    def __init__(self, model: str, apiKey: str, promptFile: str | None = None):
        super().__init__(Model("openai", model))

        self.APIKey: str = apiKey
        self.Messages: list[OllamaMessage] = []
        self.QueuePointer: int = 0

        openai.api_key = self.APIKey

    def LoadMessages(self, promptFile: str = "prompts.json") -> None:
        self.PromptFile = promptFile

        with open(promptFile, "r") as fp:
            self.Messages = json.load(fp)

    def Save(self, promptFile: str = "prompts.json") -> Any:
        try:
            with open(promptFile, "w") as fp:
                json.dump([message.ToDict() for message in self.Messages], fp, indent=2)

        except:
            print("An error occured in saving messages.")
            return self

        return self

    def Prompt(self, message: OllamaMessage):
        self.MessageQueue.append(message)

        return self

    def Run(self, *args, **kwargs):
        stream: bool | None = kwargs.get("stream")

        if stream == None:
            stream = False

        while self.QueuePointer < len(self.MessageQueue):
            self.Messages.append(self.MessageQueue[self.QueuePointer])

            response = openai.chat.completions.create(
                model=self.Model.Name,
                messages=[message.ToDict() for message in self.Messages]
                + [self.MessageQueue[self.QueuePointer].ToDict()],
            )

            if stream:
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content != None:
                        self.Messages[len(self.Messages) - 1].Content += content

                    self.OnGenerate(content)
            else:
                self.Messages[-1] = OllamaMessage(
                    "user", str(response.choices[0].message.content)
                )

            self.QueuePointer += 1

        return self
