import os

from src.tinytune.llmcontext import LLMContext
from src.tinytune.gptcontext import GPTContext, GPTMessage, Model
from src.tinytune.pipeline import Pipeline
from src.tinytune.prompt import prompt_job, PromptJob

def Main():
    context = GPTContext("gpt-4-0125-preview", str(os.getenv("OPENAI_KEY")))

    def Callback(content):
        if (content != None):
            print(content, end="")
        else:   
            print()

    @prompt_job[GPTMessage]
    def Job(id: str, context: GPTContext):
        (context.Prompt(GPTMessage("user", "hello llm"))
                .Prompt(GPTMessage("user", "you are a REST API, you will respond to JSON based requests asking for data. The response should mimic a HTTP response in form of JSON. The response should only contain the JSON, no explaination or precursor"))
                .Run(True))
        
        return context.Messages[-1] 
    
    @prompt_job[GPTMessage]
    def Job1(id: str, context: GPTContext):
        (context.Prompt(GPTMessage("user", ))
                .Run(True)) 
    
        return

    context.OnGenerateCallback = Callback

    pipeline: Pipeline[GPTMessage] = Pipeline[GPTMessage](context)

    pipeline.AddJob(Job)
    pipeline.AddJob(Job1)



Main()
