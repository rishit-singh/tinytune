from typing import Any, Callable, Union
from tinytune.llmcontext import LLMContext, Message
from functools import wraps
from types import FunctionType

class Prompt:
    """
    Represents a collection of messages and functions to execute.
    """
    def __init__(self, messages: list[dict[str, str]], functions: list[FunctionType] = []) -> None:
        """
        Initialize a Prompt object.

        Parameters:
        - messages (list[dict[str, str]]): List of messages.
        - functions (list[FunctionType]): List of functions to execute.
        """
        self.Messages: list[dict[str, str]] = messages
        self.Function: list[FunctionType] = functions

class PromptJob[MessageType: Message]:
    """
    Represents a job to execute prompts within a context.
    """
    def __init__(self, id: str, llm: LLMContext[MessageType]):
        """
        Initialize a PromptJob object.

        Parameters:
        - id (str): Identifier for the job.
        - llm (LLMContext[MessageType]): The language model context.
        """
        self.ID: str = id
        self.LLM: LLMContext[MessageType] = llm
        self.Callback: Callable[[list[Any], dict[str, Any]], None] = lambda x, y: None

    def Run(self, *args: Any, **kwdargs) -> Any:
        """
        Run the prompt job.

        Parameters:
        - args (Any): Arguments to the job.
        - kwdargs (Any): Keyword arguments to the job.

        Returns:
        - Any: Result of running the job.
        """
        return self.Callback(args, kwdargs)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """
        Call the prompt job.

        Parameters:
        - args (Any): Arguments to the job.
        - kwds (Any): Keyword arguments to the job.

        Returns:
        - Any: Result of calling the job.
        """
        return self.Run(args)


# Decorator for composing a function into a PromptJob 
def prompt_job[MessageType](id: str | None = None, context: LLMContext | None = None, prevResult: Any | None = None):
    """
    Decorator for composing a function into a PromptJob.

    Parameters:
    - id (str, optional): Identifier for the job.
    - context (LLMContext, optional): Language model context.
    - prevResult (Any, optional): Previous result.

    Returns:
    - Callable: Decorated function.
    """
    def prompt_job_inner(func: Callable[[str, LLMContext], Any]):
        @wraps(func)
        def wrapper(inner_id: str = id, llm: LLMContext = context):
            """
            Wrapper function for the decorated function.

            Parameters:
            - inner_id (str, optional): Identifier for the job.
            - llm (LLMContext, optional): Language model context.

            Returns:
            - PromptJob: Prompt job with the decorated function.
            """
            promptJob: PromptJob[MessageType] = PromptJob[MessageType](inner_id, llm) 
            promptJob.Callback = func
            return promptJob

        return wrapper

    return prompt_job_inner
