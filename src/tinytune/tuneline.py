from typing import Any
from tinytune.prompt import Prompt
from tinytune.pipeline import Pipeline
import asyncio

class TuneLine:
    def __init__(self) -> None:
        self.Pipelines: list[Pipeline]

    def AddPipeLine(self, pipeline: Pipeline) -> Any:
        self.Pipelines.append(pipeline)

        return self

    def Tune(self):
    
        return self
