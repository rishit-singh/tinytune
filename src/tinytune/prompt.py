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
    def __init__(self, callback, id: str, llm: LLMContext[MessageType], prevResult: list[Any]):
        """
        Initialize a PromptJob object.

        Parameters:
        - id (str): Identifier for the job.
        - llm (LLMContext[MessageType]): The language model context.
        """

        self.ID: str = id
        self.LLM: LLMContext[MessageType] = llm
        self.PrevResult: list[Any] = prevResult
        self.Callback: Callable[[str, LLMContext, list[Any], tuple | None, dict | None], None] = callback

    def Run(self, *args: Any, **kwargs) -> Any:
        """
        Run the prompt job.

        Parameters:
        - args (Any): Arguments to the job.
        - kwargs (Any): Keyword arguments to the job.

        Returns:
        - Any: Result of running the job.
        """
        return self.Callback(self.ID, self.LLM, self.PrevResult, *args, **kwargs) # run the callback with necessary injections

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
    - prevResult (Any, optional): Previous result.

    Returns:
    - Callable: Decorated function.
    """
    def wrapper(func: Callable[[str, LLMContext, list[Any]], Any]):
        return PromptJob[MessageType](func, id, context, None)

    return wrapper
