---
layout: default
title: Pipeline API Reference
---

# Pipeline API Reference

The `Pipeline` class manages and executes sequences of prompt jobs.

## Class Definition

```python
class Pipeline[MessageType](PromptJob[MessageType]):
    def __init__(self, llm: LLMContext):
        ...

    def AddJob(self, job: Callable[[str, LLMContext[MessageType]], Any], *args, **kwargs) -> 'Pipeline':
        ...

    def Run(self, *args, **kwargs) -> list[dict[str, str]]:
        ...

    def Save(self, promptFile: str = "prompts.json"):
        ...
```

## Methods

### `__init__(self, llm: LLMContext)`

Initializes a Pipeline object.

**Parameters:**

- `llm` (LLMContext): The language model context.

### `AddJob(self, job: Callable[[str, LLMContext[MessageType]], Any], *args, **kwargs) -> 'Pipeline'`

Adds a job to the pipeline.

**Parameters:**

- `job` (Callable[[str, LLMContext[MessageType]], Any]): The job to add.
- `*args`: Variable length argument list.
- `**kwargs`: Arbitrary keyword arguments.

**Returns:**

- Pipeline: The Pipeline object.

### `Run(self, *args, **kwargs) -> list[dict[str, str]]`

Runs the pipeline.

**Parameters:**

- `*args`: Variable length argument list.
- `**kwargs`: Arbitrary keyword arguments.

**Returns:**

- list[dict[str, str]]: Result of running the pipeline.

### `Save(self, promptFile: str = "prompts.json")`

Saves the prompts to a file.

**Parameters:**

- `promptFile` (str, optional): The file path to save the prompts to. Defaults to "prompts.json".

## Usage Example

```python
from tinytune import Pipeline, LLMContext, prompt_job

context = LLMContext(model=your_model)

@prompt_job(id="job1", context=context)
def Job1(id: str, context: LLMContext, prevResult: Any):
    return context.Prompt(Message("user", "First task")).Run().Messages[-1]

@prompt_job(id="job2", context=context)
def Job2(id: str, context: LLMContext, prevResult: Any):
    return context.Prompt(Message("user", f"Second task based on: {prevResult.Content}")).Run().Messages[-1]

pipeline = Pipeline(context)
pipeline.AddJob(Job1).AddJob(Job2)
result = pipeline.Run()

print(result)
```

For more detailed information and advanced usage, please refer to the [Pipeline documentation](../core-concepts/pipelines.md).
