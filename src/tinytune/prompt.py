from typing import Any, Callable
from types import FunctionType
from tinytune.llmcontext import LLMContext

class Prompt:
    def __init__(self, messages: list[dict[str, str]], functions: list[FunctionType] = None) -> None:
        self.Messages: list[dict[str, str]] = messages
        self.Function: list[FunctionType] = functions

class PromptJob:
    def __init__(self, id: str, llm: LLMContext, onError: Callable[[None, Exception]] = None):
        self.ID: str = id
        self.LLM: LLMContext = llm
        self.OnError: Callable[[None, Exception]] = onError

    def Run(self, *args: Any) -> Any:
        if (isinstance(args[0], LLMContext)):
            self.LLM = args[0]

        return None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.Run(args)


