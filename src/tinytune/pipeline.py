from typing import Any, Callable, TypeVar
from tinytune.prompt import PromptJob
from tinytune.llmcontext import LLMContext, Message

class Pipeline[MessageType](PromptJob[MessageType]):
    """
    Represents a pipeline of prompt jobs.
    """
    def __init__(self, llm: LLMContext):
        """
        Initialize a Pipeline object.

        Parameters:
        - llm (LLMContext): The language model context.
        """
        super().__init__(None, None, llm, None)
        self.Jobs: list[PromptJob] = list[PromptJob]()
        self.Results: dict[str, list[Any]] = dict[str, list[Any]]()
        self.LLM: LLMContext = llm
        self.IsRunning: bool = False 

    def AddJob(self, job: Callable[[str, LLMContext[MessageType]], Any]):
        """
        Add a job to the pipeline. 

        Parameters:
        - job (Callable[[str, LLMContext[MessageType]], Any]): The job to add.

        Returns:
        - Pipeline: The Pipeline object.
        """
        promptJob: PromptJob[MessageType] = job

        if promptJob.ID is None:
            promptJob.ID = f"job-{len(self.Jobs)}"
        
        if promptJob.LLM is None:
            promptJob.LLM = self.LLM
        
        self.Jobs.append(promptJob)    

        return self 

    def Run(self, *args, **kwargs) -> list[dict[str, str]]:
        """
        Run the pipeline.

        Returns:
        - list[dict[str, str]]: Result of running the pipeline.
        """
        prevResult: Any = None

        count: int = 0

        for job in self.Jobs:
            try:
                job.PrevResult = prevResult
               
                prevResult = job()
    
                if job.ID not in self.Results:
                    self.Results[job.ID] = []

                self.Results[job.ID].append(prevResult)

            except Exception as e:
                raise Exception(f"Unhandled exception occurred at job \"{job.ID}\".\nBacktrace: {[job.ID for job in self.Jobs[count:]]}")
            
            count += 1

        return prevResult
    
    def Save(self, promptFile: str = "prompts.json"):
        """
        Save the prompts to a file.
0
        Parameters:
        - promptFile (str, optional): The file path to save the prompts to.
        """
        self.LLM.Save(promptFile)
