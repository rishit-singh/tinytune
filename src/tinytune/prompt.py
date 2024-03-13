from typing import Any, Callable
from types import FunctionType
from tinytune.llmcontext import LLMContext, Message
from functools import wraps

class Prompt:
    def __init__(self, messages: list[dict[str, str]], functions: list[FunctionType] = []) -> None:
        self.Messages: list[dict[str, str]] = messages
        self.Function: list[FunctionType] = functions

class PromptJob[MessageType: Message]:
    def __init__(self, id: str, llm: LLMContext[MessageType]):
        self.ID: str = id
        self.LLM: LLMContext[MessageType] = llm
        self.Callback: Callable[[list[Any], dict[str, Any]], None] = lambda x, y : None

    def Run(self, *args: Any, **kwdargs) -> Any:
        self.Callback(args, kwdargs)

        return None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.Run(args)

# Decorator for composing a function into a PromptJob 
def prompt_job[MessageType](id: str | None = None, context: LLMContext | None = None):
    def prompt_job_inner(func: Callable[[str, LLMContext], Any]):
        def wrapper(inner_id: str = id, llm: LLMContext = context):
            promptJob: PromptJob[MessageType] = PromptJob[MessageType](inner_id, llm) 
            
            promptJob.Callback = func

            return promptJob

        return wrapper

    return prompt_job_inner

