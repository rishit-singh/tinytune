---
layout: default
title: Prompt Jobs
---

# Prompt Jobs

Prompt Jobs are a key concept in TinyTune, allowing you to encapsulate specific tasks or actions within a pipeline.

## Overview

A Prompt Job is a function decorated with `@prompt_job` that defines a specific interaction with an LLM context. It can include pre-processing, post-processing, and integration with tools.

## Defining a Prompt Job

```python
from tinytune import prompt_job, LLMContext, Message

@prompt_job(id="greet", context=your_context)
def GreetingJob(id: str, context: LLMContext, prevResult: Any):
    return (context.Prompt(Message("user", "Say hello"))
            .Run(stream=True)
            .Messages[-1])
```

## Key Components

- **Decorator**: `@prompt_job` with optional `id` and `context` parameters.
- **Function Signature**: Always includes `id`, `context`, and `prevResult` parameters.
- **Return Value**: Typically the last message from the LLM response.

## Advanced Usage

### Chaining Results

Prompt Jobs can use the `prevResult` parameter to build on the output of previous jobs in a pipeline.

```python
@prompt_job(id="elaborate", context=your_context)
def ElaborateJob(id: str, context: LLMContext, prevResult: Any):
    return (context.Prompt(Message("user", f"Elaborate on this: {prevResult.Content}"))
            .Run(stream=True)
            .Messages[-1])
```

### Integrating Tools

Prompt Jobs can incorporate tools to extend their capabilities:

```python
@prompt_job(id="weather_report", context=your_context)
def WeatherReportJob(id: str, context: LLMContext, prevResult: Any):
    weather = get_weather("New York")  # Assuming get_weather is a tool
    return (context.Prompt(Message("user", f"Describe this weather: {weather}"))
            .Run(stream=True)
            .Messages[-1])
```

For more details, see the [Prompt Job API Reference](../api-reference/prompt-job.md).
