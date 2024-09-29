import sys

import inspect
from typing import Callable
from tinytune.prompt import PromptJob


def Parse(docString: str) -> dict:
    doc = {"title": "", "params": {}}

    key = "title"

    innerKey = None

    docString = docString.replace("\n\n", "\n")

    for line in docString.split("\n"):
        line = line.strip()

        colon: int = line.find(":")

        if line == "" or line == "\n":
            continue

        if colon >= 1:
            key = "params"

            innerKey = line[0:colon]

            doc[key][innerKey] = ""

        elif colon < 0:
            if key == "title":
                doc[key] += f"{line}\n"

            elif key == "params":
                hyphen = line.find("-")

                if hyphen < 1:
                    print(key, innerKey, line)
                    doc[key][innerKey] += f"{line}\n"

                else:
                    paramKey = line[0:hyphen].strip()

                    if isinstance(doc[key][innerKey], dict):
                        doc[key][innerKey][paramKey] = line[hyphen + 1 :].strip()

                    else:
                        print(f"Setting: {key}, {innerKey}")
                        doc[key][innerKey] = {paramKey: line[hyphen + 1 :].strip()}
    return doc


def tool(func: Callable | None = None):
    def wrapper(func: Callable | None):
        if isinstance(func, PromptJob):
            spec = inspect.getfullargspec(func.Callback)

            for key in ["id", "context", "prevResult"]:
                if key in spec.annotations:
                    spec.annotations.pop(key)

            print(spec.annotations)

        else:
            spec = inspect.getfullargspec(func)

        doc = Parse(str(func.__doc__))

        meta = {
            "name": func.__name__,
            "description": doc["title"],
            "parameters": {
                "type": "object",
                "properties": doc["params"]["Args"]
                if isinstance(["params"], dict)
                else [{key: str(spec.annotations[key])} for key in spec.annotations],
            },
            "repr": func.__repr__(),
        }

        return func, meta

    return wrapper(func)
