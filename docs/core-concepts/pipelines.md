---
layout: default
title: Pipelines
---

# Pipelines

Pipelines in TinyTune manage and execute sequences of Prompt Jobs, allowing for complex workflows.

## Overview

A Pipeline is a container that maintains a queue of Prompt Jobs and runs them in sequence. The results of each job are passed to the next one in the queue.

## Creating a Pipeline

```python
from tinytune import Pipeline, LLMContext

context = LLMContext(model=your_model)
pipeline = Pipeline(context)
```

## Adding Jobs to a Pipeline

```python
pipeline.AddJob(Job1).AddJob(Job2).AddJob(Job3)
```

## Running a Pipeline

```python
result = pipeline.Run()
```

## Advanced Features

### Conditional Job Addition

You can dynamically add jobs to a pipeline based on conditions:

```python
if condition:
    pipeline.AddJob(ConditionalJob)
```

### Error Handling

Implement try-except blocks in your jobs to handle errors gracefully:

```python
@prompt_job(id="error_prone_job", context=context)
def ErrorProneJob(id: str, context: LLMContext, prevResult: Any):
    try:
        # Potentially error-prone operation
        result = some_operation()
        return context.Prompt(Message("user", f"Process this: {result}")).Run().Messages[-1]
    except SomeError as e:
        return context.Prompt(Message("user", f"An error occurred: {str(e)}")).Run().Messages[-1]
```

### Parallel Execution

While TinyTune doesn't natively support parallel job execution, you can implement it using Python's concurrent.futures:

```python
import concurrent.futures

def run_job(job, context, prevResult):
    return job(job.__name__, context, prevResult)

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(run_job, job, context, None) for job in [Job1, Job2, Job3]]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]
```

For more details, see the [Pipeline API Reference](../api-reference/pipeline.md).
