---
layout: default
title: Troubleshooting
---

# Troubleshooting

This guide addresses common issues you might encounter when using TinyTune and provides solutions to help you resolve them.

## 1. Pipeline Not Executing All Jobs

**Issue**: The pipeline stops executing before all jobs are completed.

**Possible Causes and Solutions**:

a) **Exception in a job**:

- Implement try-except blocks in your jobs to catch and handle exceptions.
- Use logging to identify where the pipeline is stopping.

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@prompt_job(id="error_prone_job", context=context)
def ErrorProneJob(id: str, context: LLMContext, prevResult: Any):
    try:
        # Your job logic here
        result = some_operation()
        logger.info(f"Job {id} completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in job {id}: {str(e)}")
        return context.Prompt(Message("user", f"An error occurred: {str(e)}")).Run().Messages[-1]
```

b) **Incorrect job chaining**:

- Ensure that each job is correctly added to the pipeline.
- Check that the output of one job is compatible with the input of the next.

## 2. LLM Context Errors

**Issue**: Errors related to LLM context initialization or API calls.

**Possible Causes and Solutions**:

a) **Invalid API key**:

- Double-check that your API key is correct and properly set.
- Use environment variables to manage API keys securely.

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
context = GPTContext("gpt-4", api_key)
```

b) **Incorrect model name**:

- Verify that you're using a valid model name for your chosen LLM provider.
- Check the documentation of your LLM provider for available models.

c) **Network issues**:

- Implement retry logic for API calls to handle temporary network issues.

```python
import time
from requests.exceptions import RequestException

def retry_api_call(func, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
```

## 3. Tool Integration Issues

**Issue**: Tools not being recognized or not functioning as expected.

**Possible Causes and Solutions**:

a) **Incorrect tool decoration**:

- Ensure that the `@tool` decorator is properly applied to your tool functions.
- Check that your tool functions have appropriate docstrings.

b) **Type mismatches**:

- Use type hints in your tool functions and ensure that the types match the actual data being passed.

```python
from typing import List, Dict

@tool
def process_data(data: List[Dict[str, Any]]) -> List[str]:
    """
    Process a list of dictionaries and return a list of strings.

    Args:
        data (List[Dict[str, Any]]): The input data to process.

    Returns:
        List[str]: The processed data as a list of strings.
    """
    # Implementation here
```

c) **External dependencies**:

- If your tools rely on external libraries or APIs, ensure they are properly installed and configured.

## 4. Memory Issues with Large Pipelines

**Issue**: Running out of memory when processing large amounts of data.

**Possible Causes and Solutions**:

a) **Accumulating large amounts of data**:

- Use generator-based approaches for handling large datasets.
- Implement streaming for large responses.

```python
def process_large_dataset(data_generator):
    for chunk in data_generator:
        yield process_chunk(chunk)

@prompt_job(id="large_data_job", context=context)
def LargeDataJob(id: str, context: LLMContext, prevResult: Any):
    data_generator = get_large_dataset()  # Assume this returns a generator
    for processed_chunk in process_large_dataset(data_generator):
        context.Prompt(Message("user", f"Process this chunk: {processed_chunk}")).Run(stream=True)
    return context.Messages[-1]
```

b) **Long-running pipelines**:

- Implement checkpointing to save intermediate results.
- Break very long pipelines into smaller sub-pipelines.

## 5. Inconsistent Results Across Runs

**Issue**: Getting different results for the same input across different runs.

**Possible Causes and Solutions**:

a) **Non-deterministic LLM responses**:

- Set a fixed seed for the LLM if supported by your provider.
- Implement result validation and retry logic for critical operations.

b) **Changing external data**:

- Implement caching for external data sources to ensure consistency during development and testing.
- Log and version external data used in your pipelines.

## 6. Slow Pipeline Execution

**Issue**: Pipelines taking longer than expected to execute.

**Possible Causes and Solutions**:

a) **Inefficient tool implementations**:

- Profile your tools to identify performance bottlenecks.
- Implement caching for expensive operations.

```python
from functools import lru_cache

@lru_cache(maxsize=100)
@tool
def expensive_operation(input_data: str) -> str:
    # Expensive operation here
    return result
```

b) **Excessive API calls**:

- Batch API calls where possible.
- Implement request throttling to avoid hitting rate limits.

c) **Large context windows**:

- Summarize or truncate previous results when passing them to the next job in the pipeline.
- Use a sliding window approach for maintaining context in long pipelines.

Remember to always check the TinyTune documentation and your LLM provider's documentation for the most up-to-date information on handling these issues. If you encounter persistent problems, consider reaching out to the TinyTune community or support channels for assistance.
