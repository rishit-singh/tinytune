import os
from tinytune.gptcontext import GPTContext, GPTMessage, Model
from tinytune.pipeline import Pipeline, PromptJob



def Main():
    context = GPTContext("gpt-4-0125-preview", os.getenv("OPENAI_KEY"))

    def Callback(content):
        if (content != None):
            print(content, end="")
        else:   
            print()

    context.OnGenerateCallback = Callback

    pipeline: Pipeline = Pipeline()

    # inp = input(">  ")

    # while (inp != "exit"):
    #     if (inp == "save"):
    #         context.Save()
            
    #         inp = input(">  ")
            
    #         continue

    #     (context.Prompt(GPTMessage("user", inp))
    #             .Run(True))

    #     inp = input(">  ")


Main()