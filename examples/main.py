import os
import sys

sys.path.append("../")

from typing import Any
from tinytune.llmcontext import LLMContext
from examples.gptcontext import GPTContext, GPTMessage, Model
from tinytune.pipeline import Pipeline
from tinytune.prompt import prompt_job, PromptJob

from PerplexityContext import PerplexityContext, PerplexityMessage


def Main():
    gptContext = GPTContext("gpt-4o", str(os.getenv("OPENAI_KEY")))
    pContext = PerplexityContext(
        "llama-3-sonar-large-32k-online", os.getenv("PERPLEXITY_KEY")
    )

    def Callback(content):
        if content != None:
            print(content, end="")
        else:
            print()

    gptContext.OnGenerateCallback = Callback
    pContext.OnGenerateCallback = Callback

    @prompt_job(id="search", context=gptContext)
    def Job(id: str, context: GPTContext, prevResult: Any):
        (
            context.Prompt(
                GPTMessage(
                    "user", f"Get me the latest top most news on f{sys.argv[1]}. "
                )
            ).Run(stream=True)
        )

        return context.Messages[-1]

    @prompt_job("extract json", context=gptContext)
    def Job1(id: str, context: GPTContext, prevResult: Any):
        (
            context.Prompt(
                GPTMessage(
                    "user",
                    f"""{prevResult.Content} extract this data into JSON, and only return the JSON, no formatting, backticks, or explanation""",
                )
            ).Run(stream=True)
        )

    pipeline: Pipeline = Pipeline(context)

    (pipeline.AddJob(Job).AddJob(Job1))

    pipeline.Run()


Main()
