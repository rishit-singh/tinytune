from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from tinytune.gptcontext import GPTContext

class ParallelRunner:
    """
    Represents a parallel runner for executing jobs concurrently.
    """
    def __init__(self, gpt: GPTContext) -> None:
        """
        Initialize a ParallelRunner object.

        Parameters:
        - gpt (GPTContext): The GPT context.
        """
        self.Jobs: list[Callable[[GPTContext, list[Any]], Any]] = []
        self.Futures: list[Future]
        self.Pool: ThreadPoolExecutor = None
        self.GPT: GPTContext = gpt
        self.Results: list = [] 

    def GetCompleted(self, onWait: Callable[[Any], Any] = None):
        """
        Get completed futures.

        Parameters:
        - onWait (Callable[[Any], Any], optional): Callback function to execute while waiting.

        Returns:
        - Iterator[Future]: Iterator of completed futures.
        """
        if onWait is not None:
            onWait(self)
        return as_completed(self.Futures)

    def OnComplete(self, *args) -> Any:
        """
        Placeholder method for actions after completion.

        Parameters:
        - args: Arbitrary arguments.

        Returns:
        - Any: Result of the completion action.
        """
        return

    def AddJob(self, job: Callable[[GPTContext, list[Any]], Any]) -> Any:
        """
        Add a job to the runner.

        Parameters:
        - job (Callable[[GPTContext, list[Any]], Any]): The job to add.

        Returns:
        - ParallelRunner: The ParallelRunner object.
        """
        self.Jobs.append(job)
        return self 

    def Run(self, onWait: Callable[[Any], Any] = None, onError: Callable[[Exception], Any] = None) -> bool:
        """
        Run the parallel runner.

        Parameters:
        - onWait (Callable[[Any], Any], optional): Callback function to execute while waiting.
        - onError (Callable[[Exception], Any], optional): Callback function to execute on error.

        Returns:
        - bool: True if successful, False otherwise.
        """
        try:
            self.Pool = ThreadPoolExecutor(max_workers=len(self.Jobs))
            self.Futures = [self.Pool.submit(job, self.GPT) for job in self.Jobs] 

            completed: list[Future] = list[Future](self.GetCompleted())

            for future in self.GetCompleted(onWait):
                self.Results.append(future.result())

            self.OnComplete()
 
        except Exception as e:
            if onError is None:
                raise e
            onError(e)

        return True
