from typing import Any, Callable
from tinytune.prompt import PromptJob
from tinytune.llmcontext import LLMContext

class Pipeline[JobType]:
    def __init__(self, llm: LLMContext):
        self.Jobs = list[Callable[[LLMContext, list[Any]]]]()
        self.Results: list[Any] = list[Any]()
        self.LLM: LLMContext = llm
        self.IsRunning: bool = False 

    def AddJob(self, job: Callable[[LLMContext, list[Any]], Any]) -> Any:
        self.Jobs.append(job)

        return self 

    def CreateJob(self, id: str) -> JobType:
        job: JobType = JobType(self.LLM)
        self.Jobs.append(job)

        return job

    def Run(self, onError: Callable[[BaseException], Any] = None) -> list[dict[str, str]]:
        prevResult: Any = None

        count: int = 0
        
        for job in self.Jobs:
            try:
                prevResult = job(prevResult)

                self.Results.append(prevResult)

            except Exception as e:
                if (job.OnError != None):
                    job.OnError(e)

                if (onError != None):
                    onError(e)
                
                    raise Exception(f"Unhandled exception occured at job {count}.\nBacktrace: {[job.ID for job in self.Jobs[count:]]}")
            
            count += 1

        return prevResult
    
    def Save(self, promptFile: str = "prompts.json"):
        self.LLM.Save(promptFile)

