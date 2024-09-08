import sys

sys.path.append("..")
sys.path.append("../src")

import inspect
from typing import Callable
from examples.parser import Parse

def tool(func):
    def wrapper(func: Callable):
        spec = inspect.getfullargspec(func)

        doc = Parse(str(func.__doc__))

        meta = {
            "name": func.__name__,
            "description": doc["title"],
            "parameters": {
                "type": "object",
                "properties": doc["params"]["Args"] if isinstance(["params"], dict) else [ { key: str(spec.annotations[key]) } for key in spec.annotations ]
            },
            "repr": func.__repr__()
        }

        return func, meta

    return wrapper(func)
