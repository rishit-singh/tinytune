from typing import Any, Callable
from tinytune.prompt import PromptJob
from tinytune.gptcontext import GPTContext
import typing

class Pipeline:
    def __init__(self, gpt: GPTContext):
        self.Jobs: list[PromptJob] = list[PromptJob]()
        self.Results: list[Any] = list[Any]()
        self.GPT: GPTContext = gpt
        self.IsRunning: bool = False 

    def AddJob(self, job: Callable[[list[Any]], Any]) -> Any:
        self.Jobs.append(job)

        return self 

    def CreateJob(self, jobType: type) -> PromptJob:
        job: type = jobType(self.GPT)
        self.Jobs.append(job)

    def Run(self, onError: Callable[[BaseException], Any] = None) -> list[dict[str, str]]:
        prevResult: Any = None

        for job in self.Jobs:
            try:
                prevResult = job(prevResult)

                self.Results.append(prevResult)
            except Exception as e:
                if (onError != None):
                    onError(e)
                raise e

        return prevResult
    
    def Save(self, promptFile: str = "prompts.json"):
        self.GPT.Save(promptFile)

