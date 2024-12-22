import os
import sys


sys.path.append("../src")
sys.path.append("../")

from dotenv import load_dotenv
from typing import Any
from tinytune.llmcontext import LLMContext
from tinytune.contexts.gptcontext import GPTContext, Model, GPTMessage
from examples.ollama_context import OllamaContext, OllamaMessage
from tinytune.pipeline import Pipeline
from tinytune.prompt import prompt_job, PromptJob

from PerplexityContext import PerplexityContext, PerplexityMessage

load_dotenv()

# gptContext = OllamaContext(f"https://api.cloudflare.com/client/v4/accounts/{os.getenv("CLOUDFLARE_ID")}/ai/v1", "@cf/meta/llama-3.1-70b-instruct", str(os.getenv("CLOUDFLARE_KEY")))

print(os.getenv("OPENAI_KEY"))
gptContext = GPTContext(model="gpt-4o-mini", apiKey=os.getenv("OPENAI_KEY"))


def Callback(content):
    if content != None:
        print(content, end="")
    else:
        print()


gptContext.OnGenerate = Callback


def Main():
    gptContext = OllamaContext("http://localhost:11434/v1/", "llama3.2:1b")
    pContext = PerplexityContext(
        "llama-3-sonar-large-32k-online", str(os.getenv("PERPLEXITY_KEY"))
    )

    def Callback(content):
        if content != None:
            print(content, end="")
        else:
            print()

    gptContext.OnGenerate = Callback
    pContext.OnGenerate = Callback

    @prompt_job(id="search", context=gptContext)
    def Job(id: str, context: GPTContext, prevResult: Any):
        (
            context.Prompt(
                OllamaMessage(
                    "user", f"Get me the latest top most news on f{sys.argv[1]}. "
                )
            ).Run(stream=True)
        )

        return context.Messages[-1]

    @prompt_job("extract json", context=gptContext)
    def Job1(id: str, context: GPTContext, prevResult: Any):
        (
            context.Prompt(
                OllamaMessage(
                    "user",
                    f"""{prevResult.Content} extract this data into JSON, and only return the JSON, no formatting, backticks, or explanation""",
                )
            ).Run(stream=True)
        )

    pipeline: Pipeline = Pipeline(context)

    (pipeline.AddJob(Job).AddJob(Job1))

    pipeline.Run()

    return pipeline


@prompt_job(id="test", context=gptContext)
def Test(id: str, context: OllamaContext, prevResult: Any, param: str):
    print("Job called: ", param)


@prompt_job(id="Chat", context=gptContext)
def Chat(id, context: GPTContext, prevResult: Any, *args):
    Running: bool = True

    while Running:
        print()

        (context.Prompt({"role": "user", "content": input("> ")}).Run(stream=True))


# Pipeline(gptContext).AddJob(Test, param="random").Run(stream=True)
gptContext.Prompt(
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                },
            },
        ],
    }
).Run(stream=True)
# Main()
