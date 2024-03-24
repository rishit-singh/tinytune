import os
import sys

sys.path.append("../")

from typing import Any
from tinytune.llmcontext import LLMContext
from tinytune.gptcontext import GPTContext, GPTMessage, Model
from tinytune.pipeline import Pipeline
from tinytune.prompt import prompt_job, PromptJob

def Main():
    context = GPTContext("gpt-4-0125-preview", str(os.getenv("OPENAI_KEY")))

    def Callback(content):
        if (content != None):
            print(content, end="")
        else:   
            print()
    
    context.OnGenerateCallback = Callback

    @prompt_job(id="job", context=context)
    def Job(id: str, context: GPTContext, prevResult: Any):
        (context.Prompt(GPTMessage("user", "you are a REST API, you will respond to JSON based requests asking for data. The response should mimic a HTTP response in form of JSON. The response should only contain the JSON, no explaination or precursor, no formatting or backticks either"))
                .Run(stream=True)
                .Prompt(GPTMessage("user", "POST \"Hello world\""))
                .Run(stream=True))
        
    @prompt_job("explainer", context)
    def Job1(id: str, context: GPTContext, prevResult: Any):
        print("prevResult: ", prevResult.ToDict())
        (context.Prompt(GPTMessage("user", f"""{prevResult.ToDict()} explain this to me"""))
                .Run(stream=True)) 


    pipeline: Pipeline = Pipeline(context)

    (pipeline.AddJob(Job)
            .AddJob(Job1))

    pipeline.Run()


Main()
