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
        self.ID: str = id
        self.__name__ = self.ID
        self.LLM: LLMContext[MessageType] = llm
        self.PrevResult: list[Any] = prevResult
        self.Callback: Callable[..., None] = callback

        # Handle initialization arguments
        ar = []
        kw = dict(kwargs)  # Create a copy of kwargs

        if len(args) >= 1:
            if len(args) >= 2:
                ar.extend(args[0])  # add args from previous one
                for key in args[1]:
                    kw[key] = args[1][key]
            else:
                ar.extend(args[0])

        self.Args = (ar, kw)

    def Run(self, args: list | None = None, kwargs: dict | None = None) -> Any:
        """
        Run the prompt job.
        """
        # Start with required params
        callArgs = [self.ID, self.LLM, self.PrevResult]

        # Add runtime positional args first
        if args:
            callArgs.extend(args)

        # Add initialization positional args
        callArgs.extend(self.Args[0])

        # Handle keyword arguments
        kwCallArgs = {}
        # Start with initialization kwargs
        kwCallArgs.update(self.Args[1])
        # Override with runtime kwargs
        if kwargs:
            kwCallArgs.update(kwargs)

        # Filter kwargs based on function signature
        params = inspect.signature(self.Callback).parameters
        filtered_kwargs = {k: v for k, v in kwCallArgs.items() if k in params}

        return self.Callback(*callArgs, **filtered_kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Called when the job is invoked like a function.
        """
        return self.Run(args=list(args), kwargs=kwargs)

def prompt_job[MessageType](id: str | None = None, context: LLMContext | None = None, *args, **kwargs):
    """
    Decorator for composing a function into a PromptJob.
    """
    def wrapper(func: Callable[..., Any]):
        return PromptJob[MessageType](func, id, context, None, args, kwargs)
    return wrapper
