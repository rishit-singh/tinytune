import os
from tinytune.gptcontext import GPTContext, GPTMessage, Model


def Main():
    context = GPTContext("gpt-4-0125-preview", os.getenv("OPENAI_KEY"))

    def Callback(content):
        if (content != None):
            print(content, end="")
        else:   
            print()


    context.OnGenerateCallback = Callback

    inp = input(">  ")
    while (inp != "exit"):
        (context.Prompt(GPTMessage("user", inp))
                .Run(True))
        inp = input(">  ")

Main()