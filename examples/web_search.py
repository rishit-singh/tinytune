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
from typing import Callable, Any
from groq import Groq
from GroqContext import WebGroqContext, WebGroqMessage

# context = WebGPTContext("gpt-4o", str(os.getenv("OPENAI_KEY")), promptFile="context.json")
context = WebGroqContext(
    "llama3-70b-8192", str(os.getenv("GROQ_KEY")), promptFile="context.json"
)

extractContext = WebGroqContext(
    "llama3-70b-8192", str(os.getenv("GROQ_KEY")), promptFile="extractContext.json"
)
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

    if textLen <= 30000:
        extractContext.Prompt(WebGroqMessage("user", f"START\n{parser.Text}\nEND"))
    else:
        for x in range(0, textLen, 30000):
            if x == 0:
                extractContext.Prompt(
                    WebGroqMessage("user", f"START\n{parser.Text[x:30000]}")
                )
            elif textLen - x <= 30000:
                extractContext.Prompt(
                    WebGroqMessage("user", f"\n{parser.Text[x:]}\nEND")
                )
            else:
                extractContext.Prompt(WebGroqMessage("user", parser.Text[x:30000]))

    return (extractContext.Run(stream=True).Messages[-1].Content, url)


context.OnGenerateCallback = Callback
context.OnFetch = OnFetch


@prompt_job(id="setup", context=extractContext)
def Setup(id: str, context: WebGroqContext, prevResult: Any):
    (
        context.Prompt(
            WebGroqMessage(
                "system",
                """
            You're a text extractor, you take long news article texts with a bunch of text content. You're supposed to extract just the actual article content from it and not the remaining text scraped from the webpage.

            The text can be split into multple prompts so look out for the word START to see where the text starts, and END for where it ends. If a message doesnt contain END, that means there's still more text to come.

            You return the text in form of json, using the following schema: {'title':'', metadata:{}, 'content': ''}.
        """,
            )
        )
        .Run(stream=True)
        .Save()
    )

    return context.Messages[-1]


@prompt_job(id="fetch", context=context)
def Fetch(id: str, context: WebGroqContext, prevResult: Any):
    (
        context.Prompt(
            WebGroqMessage(
                "system",
                "You're a web fetcher. You fetch the web pages from the URLs given to you",
            )
        )
        .PromptSearch(
            "https://www.foxnews.com/politics/biden-dodges-answering-whether-hed-take-neurological-test-no-one-said-i-had-to"
        )
        .PromptSearch(
            "https://www.pbs.org/newshour/politics/elected-democrats-admit-biden-had-poor-debate-performance-but-reject-talk-of-replacement"
        )
        .Run(stream=True)
        .Save()
    )

    return (context.Messages[-1].Content, context.Messages[-3].Content)


@prompt_job(id="compare", context=context)
def Compare(id: str, context: WebGroqContext, prevResult: Any):
    context.Prompt(
        WebGroqMessage(
            "user", "Now compare these two articles based on how biased they are."
        )
    ).Run(stream=True).Save()
    return context.Messages[-1].Content


@prompt_job(id="extract", context=extractContext)
def Extract(id: str, context: WebGroqContext, prevResult: Any):
    (
        context.Prompt(
            WebGroqMessage(
                "system",
                """
            You're a text extractor, you take long news article texts with a bunch of irrelevant strings in it, and extract only the important info.

            The text can be split up into multiple messages. So look for the text START to see where the text starts, and END for where it ends. If a message doesnt contain END, that means there's still more text to come.

            You return the text in form of json, using the following schema: {'title':'', metadata:{}, 'content': ''}.
        """,
            )
        )
        .Run(stream=True)
        .Save()
    )

    return context.Messages[-1]


@prompt_job(id="jsonify", context=context)
def Jsonify(id: str, context: WebGroqContext, prevResult: str):
    print("\n")

    jsonModel = {
        "analysis": [
            {
                "id": 0,
                "article": {"title": "", "url": "original fetched URL"},
                "analysis": {},
            }
        ],
        "opinions": {"neutral": "", "honest": "", "factual": ""},
    }

    context.Prompt(
        WebGroqMessage(
            "user",
            f"Now jsonify this analysis in the format NO BACKTICKS {json.dumps(jsonModel)}\n{prevResult}",
        )
    ).Run(stream=True)

    return context.Messages[-1].Content


@prompt_job("opinions", context)
def GetOpinions(id: str, context: WebGroqContext, prevResult: str):
    return (
        context.Prompt(
            WebGroqMessage(
                "user",
                "Give your honest opinions on the situation along with a factually correct and neutral stance.",
            )
        )
        .Run(stream=True)
        .Messages[-1]
        .Content
    )


start = time.time()

pipeline = Pipeline(extractContext)

(
    pipeline.AddJob(Setup)
    .AddJob(Fetch)
    .AddJob(GetOpinions)
    .AddJob(Compare)
    .AddJob(Jsonify)
    .Run(stream=True)
)

print(
    "\n\nFinal parsed: ",
    json.dumps(json.loads(pipeline.Results["jsonify"][-1]), indent=2),
)

print("Time elapsed: ", time.time() - start)
