from tinytune.prompt import PromptJob, prompt_job
from tinytune.llmcontext import Model
from  tinytune.pipeline import Pipeline
from gptcontext import GPTContext, GPTMessage

from ReplicateContext import ReplicateContext, ReplicateMessage

from typing import Any
import re
import json
import sys
import os
import asyncio

def Callback(content):
    if (content != None):
        print(content, end="")
    else:   
        print()
    
def LoadMessages(path: str, max: int, user: str) -> list[ReplicateMessage]:
    prompts: list[ReplicateMessage] = []

    with open(path, 'r') as fp:
        for message in json.load(fp)["messages"][:max]:
            if (message["author"]["name"] == user):
                regex = re.compile(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')

                if regex.search(message['content']):
                    continue

                prompts.append(ReplicateMessage("user", message["content"]))

            else:
                prompts.append(ReplicateMessage("assistant", message["content"]))

    return prompts 

    
llm: ReplicateContext = ReplicateContext(Model("mistralai", "mistral-7b-instruct-v0.2"), os.getenv("REPLICATE_KEY"), "discord_ai_prompt_context.txt")
# llm: GPTContext = GPTContext("gpt-4-0125-preview", str(os.getenv("OPENAI_KEY"))) 
llm.OnGenerateCallback = Callback

messages = LoadMessages(sys.argv[1], int(sys.argv[2]), sys.argv[3])

@prompt_job(id="build_context", context=llm)
def BuildContext(id: str, context: ReplicateContext, prevResult: Any):
    for message in messages:
        context.Messages.append(message)

    context.Run(stream=True).Save()
    print("Context built")

@prompt_job(id="chatbot", context=llm)
def RunChatBot(id: str, context: ReplicateContext, prevResult: Any):
    inp = input("> ")
    while (inp != "exit"):
        context.Prompt(ReplicateMessage("user", inp))
        context.Run(stream=True)
        print()
        inp = input("> ")

discordAI: Pipeline = Pipeline(llm)

(discordAI.AddJob(BuildContext)
    .AddJob(RunChatBot)
    .Run())

