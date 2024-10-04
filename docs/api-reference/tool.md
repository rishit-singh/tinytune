---
layout: default
title: tool Decorator API Reference
---

# tool Decorator API Reference

The `tool` decorator is used to create tools that can be used within prompt jobs to extend the capabilities of the language model.

## Decorator Definition

```python
def tool(func: Callable | None = None):
    ...
```

## Parameters

- `func` (Callable | None, optional): The function to be decorated.

## Usage

The `tool` decorator is used to wrap functions that provide specific functionality. These functions can then be called within prompt jobs. The decorator extracts metadata from the function's docstring and type hints.

## Example

```python
from tinytune.tool import tool

@tool
def get_weather(location: str) -> str:
    """
    Gets the weather for a given location.

    Args:
        location (str): The location to get weather for.

    Returns:
        str: A string describing the weather.
    """
    # Implementation here
    return f"Sunny, 25°C in {location}"
```

## Notes

- The decorated function should have a clear and descriptive docstring.
- Use type hints to specify the expected types of arguments and return values.
- The tool can be used within prompt jobs to perform specific tasks or retrieve information.

## Using Tools in Prompt Jobs

```python
from tinytune import prompt_job, LLMContext, Message

@prompt_job(id="weather_report", context=your_context)
def WeatherReportJob(id: str, context: LLMContext, prevResult: Any):
    location = "New York"
    weather = get_weather(location)
    return (context.Prompt(Message("user", f"Describe this weather in {location}: {weather}"))
            .Run(stream=True)
            .Messages[-1])
```

For more detailed information and advanced usage, please refer to the [Tools documentation](../core-concepts/tools.md).

```

This completes the API reference section of the documentation. The structure and content provided here offer a comprehensive guide to using TinyTune, from basic concepts to advanced usage, troubleshooting, and detailed API references. Users can navigate through these documents to find the information they need to effectively use and understand the TinyTune library.
```
