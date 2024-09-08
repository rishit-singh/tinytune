import json
from tinytune.llmcontext import LLMContext, Model, Message
from typing import Callable, Any
from groq import Groq


class WebGroqMessage(Message):
    __slots__ = ("Role", "Content", "Type")

    def __init__(self, role: str, content: str, type: str = "message"):
        super().__init__(role, content)
        self.Type = type


class WebGroqContext(LLMContext[WebGroqMessage]):
    def __init__(self, model: str, apiKey: str, promptFile: str | None = None):
        super().__init__(Model("groq", model))

        self.APIKey: str = apiKey
        self.Messages: list[WebGroqMessage] = []
        self.QueuePointer: int = 0

        self.client = Groq(api_key=self.APIKey)

        self.OnFetch = lambda content, url: (content, URL)

        self.PromptFile = promptFile

        self.Prompt(
            WebGroqMessage(
                "system",
                "You are a web search assistant. When given a URL, respond with 'FETCH:' followed by the URL.",
            )
        )

    def LoadMessages(self, promptFile: str = "prompts.json") -> None:
        self.PromptFile = promptFile

        with open(promptFile, "r") as fp:
            self.Messages = json.load(fp)

    def Save(self, promptFile: str = "prompts.json") -> Any:
        try:
            promptFile = promptFile if self.PromptFile == None else self.PromptFile

            with open(promptFile, "w") as fp:
                json.dump([message.ToDict() for message in self.Messages], fp, indent=2)

        except:
            print("An error occurred in saving messages.")
            return self

        return self

    def Prompt(self, message: WebGroqMessage):
        self.MessageQueue.append(message)
        return self

    def FetchURL(self, url):
        return self.OnFetch(str(requests.get(url).content), url)

    def PromptSearch(self, query: str):
        self.Prompt(WebGroqMessage("user", query, "search_message"))
        return self

    def Run(self, *args, **kwargs):
        stream: bool | None = kwargs.get("stream")

        if stream is None:
            stream = False

        while self.QueuePointer < len(self.MessageQueue):
            self.Messages.append(self.MessageQueue[self.QueuePointer])

            isSearchMessage: bool = self.Messages[-1].Type == "search_message"

            messages = [message.ToDict() for message in self.Messages] + [
                self.MessageQueue[self.QueuePointer].ToDict()
            ]

            try:
                response = self.client.chat.completions.create(
                    model=self.Model.Name,
                    messages=messages,
                    temperature=0,
                    stream=stream,
                )

                content = ""
                if stream:
                    for chunk in response:
                        chunk_content = chunk.choices[0].delta.content
                        if chunk_content is not None:
                            content += chunk_content
                            self.OnGenerateCallback(chunk_content)
                else:
                    content = response.choices[0].message.content
                    self.OnGenerateCallback(content)

                if content != "" and content:
                    self.Messages.append(WebGroqMessage("assistant", ""))
                    self.Messages[-1].Content = content

                # Handle search messages with manual function call
                if isSearchMessage and content.startswith("FETCH:"):
                    url = content[6:].strip()
                    fetched_content = self.FetchURL(url)
                    self.Messages.append(
                        WebGroqMessage(
                            "assistant",
                            f"Fetched content from {url}: {fetched_content}",
                        )
                    )

            except Exception as e:
                print(f"An error occurred: {e}")

            self.QueuePointer += 1

        return self
