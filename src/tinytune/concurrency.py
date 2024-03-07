from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from tinytune.gptcontext import GPTContext

class ParallelRunner:
    def __init__(self, gpt: GPTContext) -> None:
        self.Jobs: list[Callable[[GPTContext, list[Any]], Any]] = []
        self.Futures: list[Future]
        self.Pool: ThreadPoolExecutor = None
        self.GPT: GPTContext = gpt
        self.Results: list = [] 

    def GetCompleted(self,  onWait: Callable[[Any], Any] = None):
        if (onWait != None):
            onWait(self)
        return as_completed(self.Futures)

    def OnComplete(self, *args) -> Any:
        return

    def AddJob(self, job: Callable[[GPTContext, list[Any]], Any]) -> Any:
        self.Jobs.append(job)
        return self 

    def Run(self, onWait: Callable[[Any], Any] = None, onError: Callable[[Exception], Any] = None) -> bool:
        try:
            self.Pool = ThreadPoolExecutor(max_workers=len(self.Jobs))
            self.Futures = [self.Pool.submit(job, self.GPT) for job in self.Jobs] 

            print(f"Futures: {len(self.Futures)}")

            completed: list[Future] = list[Future](self.GetCompleted())

            for future in self.GetCompleted(onWait):
                self.Results.append(future.result())

            self.OnComplete()
 
        except Exception as e :
            if (onError == None):
                raise e
            onError(e)

        return True

 