import os
import sys
import openai
import json
import html.parser
import time

import requests
from gptcontext import GPTContext, GPTMessage
from tinytune.prompt import PromptJob, prompt_job

from tinytune import Pipeline
from tinytune.util.prompt import ValidatePrompt
from tinytune.llmcontext import LLMContext, Model, Message
from typing import Callable, Any
from groq import Groq

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

        self.OnFetch = lambda content, url : (content, url)

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
        return self.OnFetch(str(requests.get(url).content), url)


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
                        # continue

                else:
                    for chunk in response:
                        content = chunk.choices[0].delta.content
                        if content != None:
                            self.Messages[len(self.Messages) - 1].Content += content

                        self.OnGenerateCallback(content)

            self.QueuePointer += 1

        return self

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

        self.OnFetch = lambda content, url : (content, URL)

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

            isSearchMessage: bool = (self.Messages[-1].Type == "search_message")

            messages = [message.ToDict() for message in self.Messages] + [self.MessageQueue[self.QueuePointer].ToDict()]


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

                self.Messages[-1].Content = content

                # Handle search messages with manual function call
                if isSearchMessage and content.startswith("FETCH:"):
                    url = content[6:].strip()
                    fetched_content = self.FetchURL(url)
                    self.Messages.append(WebGroqMessage("assistant", f"Fetched content from {url}: {fetched_content}"))

            except Exception as e:
                print(f"An error occurred: {e}")

            self.QueuePointer += 1

        return self

# context = WebGPTContext("gpt-4o", str(os.getenv("OPENAI_KEY")), promptFile="context.json")
context = WebGroqContext("llama3-70b-8192", str(os.getenv("GROQ_KEY")), promptFile="context.json")
extractContext = WebGroqContext("llama3-70b-8192", str(os.getenv("GROQ_KEY")), promptFile="extractContext.json")
# extractContext = GPTContext("gpt-4o", str(os.getenv("OPENAI_KEY")), promptFile="extractContext.json")

class Parser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.Text: str = ""

    def handle_data(self, data: str) -> None:
        self.Text += data


def Callback(content):
    if content != None:
        print(content, end="")
    else:
        print()

extractContext.OnGenerateCallback = Callback

def OnFetch(content: str, url: str) -> tuple:
    parser = Parser()

    parser.feed(content)

    textLen = len(parser.Text)

    if (textLen <=30000):
        extractContext.Prompt(WebGroqMessage("user", f"START\n{parser.Text}\nEND"))
    else:
        for x in range(0, textLen, 30000):
            if (x == 0):
                extractContext.Prompt(WebGroqMessage("user", f"START\n{parser.Text[x:30000]}"))
            elif (textLen - x <= 30000):
                extractContext.Prompt(WebGroqMessage("user", f"\n{parser.Text[x:]}\nEND"))
            else:
                extractContext.Prompt(WebGroqMessage("user", parser.Text[x:30000]))

    return (extractContext.Run(stream=True).Messages[-1].Content, url)


context.OnGenerateCallback = Callback
context.OnFetch = OnFetch

@prompt_job(id="setup", context=extractContext)
def Setup(id: str, context: WebGroqContext, prevResult: Any):
    (context.Prompt(WebGroqMessage("system", """
            You're a text extractor, you take long news article texts with a bunch of text content. You're supposed to extract just the actual article content from it and not the remaining text scraped from the webpage.

            The text can be split into multple prompts so look out for the word START to see where the text starts, and END for where it ends. If a message doesnt contain END, that means there's still more text to come.

            You return the text in form of json, using the following schema: {'title':'', metadata:{}, 'content': ''}.
        """)).Run(stream=True).Save())

    return context.Messages[-1]

@prompt_job(id="fetch", context=context)
def Fetch(id: str, context: WebGroqContext, prevResult: Any):
    (context.Prompt(WebGroqMessage("system", "You're a web fetcher. You fetch the web pages from the URLs given to you"))
            .PromptSearch("https://www.cnn.com/2024/06/26/tech/al-michaels-ai-olympics/index.html")
            .PromptSearch("https://www.ctvnews.ca/sci-tech/nbc-to-use-ai-version-of-announcer-al-michaels-voice-for-olympics-recaps-1.6942177")
            .Run(stream=True).Save())

    return (context.Messages[-1].Content, context.Messages[-3].Content)

@prompt_job(id="compare", context=context)
def Compare(id: str, context: WebGroqContext, prevResult: Any):
    context.Prompt(WebGroqMessage("user", "Now compare these two articles based on how biased they are.")).Run(stream=True).Save()
    return context.Messages[-1].Content

@prompt_job(id="extract", context=extractContext)
def Extract(id: str, context: WebGroqContext, prevResult: Any):
    (context.Prompt(WebGroqMessage("system", """
            You're a text extractor, you take long news article texts with a bunch of irrelevant strings in it, and extract only the important info.

            The text can be split up into multiple messages. So look for the text START to see where the text starts, and END for where it ends. If a message doesnt contain END, that means there's still more text to come.

            You return the text in form of json, using the following schema: {'title':'', metadata:{}, 'content': ''}.
        """)).Run(stream=True).Save())

    return context.Messages[-1]

@prompt_job(id="jsonify", context=context)
def Jsonify(id: str, context: WebGroqContext, prevResult: str):
    print('\n')

    jsonModel = [
        {
            "id": 0,
            "article": {
                "title": "",
                "url": "original fetched URL"
            },
            "analysis": {}
        }
    ]

    context.Prompt(WebGroqMessage("user", f"Now jsonify this analysis in the formatNO BACKTICKS {json.dumps(jsonModel)}\n{prevResult}")).Run(stream=True)


start = time.time()

pipeline = Pipeline(extractContext)

(pipeline.AddJob(Setup)
        .AddJob(Fetch)
        .AddJob(Compare)
        .AddJob(Jsonify)
        .Run(stream=True))


print("Time elapsed: ", time.time() - start)
