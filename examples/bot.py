import os
from gptcontext import GPTContext

running: bool = False
def RunBot():
    context: GPTContext = GPTContext("gpt-4", os.getenv("OPENAI_KEY"))
    running = True

    while (running):
        prompt = input("> ")
        print(context.Prompt(prompt)[-1]["content"])
RunBot()
