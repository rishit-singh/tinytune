from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from tinytune.llmcontext import LLMContext


class ParallelRunner:
    """
    Represents a parallel runner for executing jobs concurrently.
    """

    def __init__(self, llm: LLMContext) -> None:
        """
        Initialize a ParallelRunner object.

        Parameters:
        - gpt (LLMContext): The GPT context.
        """
        self.Jobs: list[Callable[[LLMContext, list[Any]], Any]] = []
        self.Futures: list[Future]
        self.Pool: ThreadPoolExecutor = None
        self.GPT: LLMContext = llm
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

    def AddJob(self, job: Callable[[LLMContext, list[Any]], Any]) -> Any:
        """
        Add a job to the runner.

        Parameters:
        - job (Callable[[LLMContext, list[Any]], Any]): The job to add.

        Returns:
        - ParallelRunner: The ParallelRunner object.
        """
        self.Jobs.append(job)
        return self

    def Run(self, onWait: Callable[[Any], Any] = None) -> bool:
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

            for future in self.GetCompleted(onWait):
                self.Results.append(future.result())

            self.OnComplete()

        except Exception as e:
            raise e

        return True
