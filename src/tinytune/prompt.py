import inspect
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
    def __init__(self, callback, id: str, llm: LLMContext[MessageType], prevResult: list[Any], *args, **kwargs):
        """
        Initialize a PromptJob object.

        Parameters:
        - id (str): Identifier for the job.
        - llm (LLMContext[MessageType]): The language model context.
        """

        self.ID: str = id
        self.LLM: LLMContext[MessageType] = llm
        self.PrevResult: list[Any] = prevResult
        self.Callback: Callable[..., None] = callback

        kw = kwargs
        ar = []

        l = len(args)

        if (len(args) >= 1):
            if (len(args) >= 2):
                ar.extend(args[0])
                for key in args[1]:
                    kw[key] = args[1][key]
            else:
                ar.extend(args[0])

        self.Args = (ar, kw)

    def Run(self, *args: Any) -> Any:
        """
        Run the prompt job.

        Parameters:
        - args (Any): Arguments to the job.
        - kwargs (Any): Keyword arguments to the job.

        Returns:
        - Any: Result of running the job.
        """

        callArgs = list([ self.ID, self.LLM, self.PrevResult ]) # required params
        callArgs.extend(args[0])
        callArgs.extend(self.Args[0])

        kwCallArgs = args[1]
        kwargs = self.Args[1]

        for key in kwargs:
            kwCallArgs[key] = kwargs[key]

        params = inspect.signature(self.Callback).parameters

        for key in args[1]:
            if (key in params):
                return self.Callback(*callArgs, **kwCallArgs)

        return self.Callback(*callArgs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Parameters:
        - args (Any): Arguments to the job.
        - kwargs (Any): Keyword arguments to the job.

        Returns:
        - Any: Result of calling the job.
        """

        return self.Run(args, kwargs)

def prompt_job[MessageType](id: str | None = None, context: LLMContext | None = None, *args, **kwargs):
    """
    Decorator for composing a function into a PromptJob.

    Parameters:
    - id (str, optional): Identifier for the job.
    - context (LLMContext, optional): Language model context.
    - prevResult (Any, optional): Previous result
    Returns:
    - Callable: Decorated function.
    """
    def wrapper(func: Callable[..., Any]):
        return PromptJob[MessageType](func, id, context, None, args, kwargs)

    return wrapper
