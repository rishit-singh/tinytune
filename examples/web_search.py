import os
import sys
import openai
import json

import requests
from tinytune.util.prompt import ValidatePrompt
from tinytune.llmcontext import LLMContext, Model, Message
from typing import Callable, Any

class WebGPTMessage(Message):
    __slots__ = ("Role", "Content", "Type")

    def __init__(self, role: str, content: str, type: str = "message"):
        super().__init__(role, content)
        self.Type = type


class WebGPTContext(LLMContext[WebGPTMessage]):
    def __init__(self, model: str, apiKey: str, promptFile: str | None = None):
        super().__init__(Model("openai", model))

        self.APIKey: str = apiKey
        self.Messages: list[WebGPTMessage] = []
        self.QueuePointer: int = 0

        openai.api_key = self.APIKey

        # self.OnFetch = lambda x : None

        self.Functions = [
            {
                "name": "FetchURL",
                "description": "Fetches content from a URL",
                "parameters": {
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"],
                },
            },
        ]

        self.Prompt(
            WebGPTMessage(
                "system",
                "You are a web search assistant. You search the web for the given urls.",
            )
        )

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

    def Prompt(self, message: WebGPTMessage):
        self.MessageQueue.append(message)

        return self

    def FetchURL(self, url):
        return str(requests.get(url).content)

    def PromptSearch(self, query: str):
        self.Prompt(WebGPTMessage("user", query, "search_message"))
        return self


    def Run(self, *args, **kwargs):
        stream: bool | None = kwargs.get("stream")

        if stream == None:
            stream = False

        while self.QueuePointer < len(self.MessageQueue):
            self.Messages.append(self.MessageQueue[self.QueuePointer])

            isSearchMessage: bool = (
                self.Messages[-1].Type == "search_message"
            )

            if isSearchMessage:
                print("Functions: ", self.Functions)
                print("Function call", {
                    "name": "FetchURL",
                    "arguments": json.dumps({"url": self.Messages[-1].Content}),
                })

                response = openai.chat.completions.create(
                    model=self.Model.Name,
                    messages=[message.ToDict() for message in self.Messages]
                    + [self.MessageQueue[self.QueuePointer].ToDict()],
                    temperature=0,
                    stream=stream,
                    functions=self.Functions,
                    function_call={
                        "name": "FetchURL",
                        "arguments": json.dumps({"url": self.Messages[-1].Content}),
                    },
                )

            else:
                response = openai.chat.completions.create(
                    model=self.Model.Name,
                    messages=[message.ToDict() for message in self.Messages]
                    + [self.MessageQueue[self.QueuePointer].ToDict()],
                    temperature=0,
                    stream=stream,
                    functions=self.Functions,
                )

            functionCall = {"name": "", "arguments": "" }

            if stream:
                if isSearchMessage:
                    for res in response:
                        delta = res.choices[0].delta
                        if delta.function_call != None:
                            if delta.function_call.name != None:
                                functionCall["name"] = delta.function_call.name
                            if delta.function_call.arguments:
                                functionCall["arguments"] += delta.function_call.arguments

                        if res.choices[0].finish_reason != None:
                            print("Calling the function")

                            args = dict(json.loads(functionCall["arguments"]))
                            if functionCall["name"] == "FetchURL":
                                    self.Messages.append(WebGPTMessage("assistant", f"Fetched {self.FetchURL(args["url"])}"))
                            break

                        # if not delta.get("content", None):
                        #     continue

                else:
                    for chunk in response:
                        content = chunk.choices[0].delta.content
                        if content != None:
                            self.Messages[len(self.Messages) - 1].Content += content

                        self.OnGenerateCallback(content)

            self.QueuePointer += 1

        return self

context = WebGPTContext("gpt-4o", str(os.getenv("OPENAI_KEY")))

def Callback(content):
    if content != None:
        print(content, end="")
    else:
        print()

context.OnGenerateCallback = Callback

(context.Prompt(WebGPTMessage("user", "hello gpt"))
        .PromptSearch("https://www.wsj.com/tech/tesla-wins-chinas-backing-for-driver-assistance-service-20816802")
        .PromptSearch("https://www.cnn.com/2024/04/29/cars/elon-musk-surprise-visit-china-premier-li-intl-hnk/index.html")
        .Prompt(WebGPTMessage("user", "Compare these two articles and tell me which one is more biased against Elon Musk."))
        .Run(stream=True))

# def execute_function(response):
#     function_call = response.choices[0].message.function_call
#     if function_call.name == "fetch_url":
#         arguments = json.loads(function_call.arguments)
#         url = arguments["url"]
#         return fetch_url(url)


# def call_openai_function(url):
#     response = openai.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "You are an assistant that helps fetch data from the internet.",
#             },
#             {"role": "user", "content": f"Fetch the content from {url}"},
#         ],
#         functions=functions,
#         function_call={"name": "fetch_url", "arguments": json.dumps({"url": url})},
#     )

#     return response


# # Example usage
# url = "https://google.com"
# response = call_openai_function(url)
# print(response)
# result = execute_function(response)
# print(result)
