import os
import sys

sys.path.append("../")

from typing import Any
from tinytune.llmcontext import LLMContext
from tinytune.gptcontext import GPTContext, GPTMessage, Model
from tinytune.pipeline import Pipeline
from tinytune.prompt import prompt_job, PromptJob
from PerplexityContext import PerplexityContext, PerplexityMessage

def Main():
    context = GPTContext("gpt-4-0125-preview", str(os.getenv("OPENAI_KEY")))
    pContext = PerplexityContext("pplx-70b-online", os.getenv("PERPLEXITY_KEY"))

    def Callback(content):
        if (content != None):
            print(content, end="")
        else:   
            print()
    
    context.OnGenerateCallback = Callback
    pContext.OnGenerateCallback = Callback

    @prompt_job(id="search", context=pContext)
    def Job(id: str, context: PerplexityContext, prevResult: Any):
        (context.Prompt(PerplexityMessage("user", "Find me Japanese restaurants in Vancouver"))
                .Run(stream=True))

        return context.Messages[-1]

    @prompt_job("extract json", context)
    def Job1(id: str, context: GPTContext, prevResult: Any):
        print("prevResult: ", prevResult.ToDict())
        (context.Prompt(GPTMessage("user", f"""{prevResult.Content} extract this data into JSON, and only return the JSON, no formatting, backticks, or explanation"""))
                .Run(stream=True)) 

    pipeline: Pipeline = Pipeline(context)

    (pipeline.AddJob(Job)
            .AddJob(Job1))

    pipeline.Run()


Main()
