from typing import Any, Callable, TypeVar
from tinytune.prompt import PromptJob
from tinytune.llmcontext import LLMContext, Message

class Pipeline[MessageType](PromptJob[MessageType]):
    def __init__(self, llm: LLMContext):
        self.Jobs: list[PromptJob] = list[PromptJob]()
        self.Results: dict[str, list[Any]] = dict[str, list[Any]]()
        self.LLM: LLMContext = llm
        self.IsRunning: bool = False 

    def AddJob(self, job: Callable[[str, LLMContext[MessageType]], Any]):
        promptJob: PromptJob[MessageType] = job()

        if (promptJob.ID == None):
            promptJob.ID = f"job-{len(self.Jobs)}"
        
        if (promptJob.LLM == None):
            promptJob.LLM = self.LLM
        
        self.Jobs.append(promptJob)    

        return self 

    def Run(self, *args, **kwargs) -> list[dict[str, str]]:
        prevResult: Any = None

        count: int = 0
        
        for job in self.Jobs:
            try:
                prevResult = job(llm=self.LLM, prev_result=prevResult)

                if (not(job.ID in self.Results.keys())):
                    self.Results[job.ID] = []

                self.Results[job.ID].append(prevResult)

            except Exception as e:
                raise Exception(f"Unhandled exception occured at job {count}.\nBacktrace: {map(lambda job : f"{job}\n", [job.ID for job in self.Jobs[count:]])}")
            
            count += 1

        return prevResult
    
    def Save(self, promptFile: str = "prompts.json"):
        self.LLM.Save(promptFile)

