from typing import Any
from peregrinegpt.gptcontext import GPTContext
from peregrinegpt.web.scraping import DataScraper
from types import FunctionType

class OpenAIFunction:
    def __init__(self, func: FunctionType) -> None:
        self.Function = func

    def GetDefinition(self):
        params: dict = self.Function.__annotations__

        return dict({
            "name": self.Function.__name__,
            "parameters": params
        })

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

class Prompt:
    def __init__(self, messages: list[dict[str, str]], functions: list[FunctionType] = None) -> None:
        self.Messages: list[dict[str, str]] = messages
        self.Function: list[FunctionType] = functions


class PromptJob:
    def __init__(self, gpt: GPTContext):
        self.GPT: GPTContext = gpt
        pass

    def Run(self, args: list[Any] = None) -> Any:
        return

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.Run(args[0])
 
 
