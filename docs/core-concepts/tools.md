---
layout: default
title: Tools
---

# Tools

Tools in TinyTune extend the capabilities of your language model by allowing it to perform specific actions or retrieve information.

## Overview

A Tool is a function decorated with `@tool` that can be called within Prompt Jobs to perform specific tasks.

## Creating a Tool

```python
from tinytune.tool import tool

@tool
def get_weather(location: str):
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

## Key Components

- **Decorator**: `@tool`
- **Docstring**: Describes the tool's functionality, arguments, and return value.
- **Type Hints**: Helps with automatic parameter validation.

## Using Tools in Prompt Jobs

```python
@prompt_job(id="weather_report", context=your_context)
def WeatherReportJob(id: str, context: LLMContext, prevResult: Any):
    weather = get_weather("New York")
    return (context.Prompt(Message("user", f"Describe this weather: {weather}"))
            .Run(stream=True)
            .Messages[-1])
```

## Advanced Tool Usage

### Complex Tools with Multiple Methods

You can create more complex tools by combining multiple methods in a class:

```python
class WeatherTool:
    @tool
    def get_current_weather(self, location: str):
        """Get current weather for a location."""
        # Implementation

    @tool
    def get_forecast(self, location: str, days: int):
        """Get weather forecast for a location."""
        # Implementation

    def get_function_map(self):
        return {name: func for name, func in vars(self.__class__).items() if isinstance(func, tuple)}

    def call_method(self, function_call):
        function_name = function_call.get("function")
        params = function_call.get("params", {})
        params["self"] = self

        function_map = self.get_function_map()
        if function_name not in function_map:
            raise ValueError(f"Function '{function_name}' not found")

        return function_map[function_name][0](**params)

weather_tool = WeatherTool()
```

### Error Handling in Tools

Implement proper error handling in your tools to ensure robustness:

```python
@tool
def divide_numbers(a: float, b: float):
    """
    Divides two numbers.
    Args:
        a (float): Numerator
        b (float): Denominator
    Returns:
        float: Result of a / b
    """
    try:
        return a / b
    except ZeroDivisionError:
        return "Error: Cannot divide by zero"
```

For more details, see the [Tool API Reference](../api-reference/tool.md).

```

```
