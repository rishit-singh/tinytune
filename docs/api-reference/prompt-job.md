---
layout: default
title: prompt_job Decorator API Reference
---

# prompt_job Decorator API Reference

The `prompt_job` decorator is used to create prompt jobs for use in pipelines.

## Decorator Definition

```python
def prompt_job[MessageType](id: str | None = None, context: LLMContext | None = None, *args, **kwargs):
    ...
```

## Parameters

- `id` (str | None, optional): Identifier for the job.
- `context` (LLMContext | None, optional): The language model context.
- `*args`: Variable length argument list.
- `**kwargs`: Arbitrary keyword arguments.

## Usage

The `prompt_job` decorator is used to wrap functions that define specific interactions with an LLM context. The decorated function should have the following signature:

```python
def job_function(id: str, context: LLMContext, prevResult: Any) -> Any:
    ...
```

## Example

```python
from tinytune import prompt_job, LLMContext, Message

@prompt_job(id="summarize", context=your_context)
def SummarizeJob(id: str, context: LLMContext, prevResult: Any):
    return (context.Prompt(Message("user", f"Summarize this: {prevResult.Content}"))
            .Run(stream=True)
            .Messages[-1])
```

## Notes

- The `id` parameter, if provided, should be unique within a pipeline.
- If `context` is not provided in the decorator, it should be provided when adding the job to a pipeline.
- The decorated function will be converted into a `PromptJob` object, which can be added to a `Pipeline`.

For more detailed information and advanced usage, please refer to the [Prompt Jobs documentation](../core-concepts/prompt-jobs.md).
