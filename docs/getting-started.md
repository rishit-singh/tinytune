---
layout: default
title: Getting Started
---

# Getting Started with TinyTune

This guide will walk you through creating a simple TinyTune workflow.

## Prerequisites

Ensure you have TinyTune installed. If not, refer to the [Installation Guide](installation.md).

## Basic Usage

1. Import necessary components:

   ```python
   from tinytune import LLMContext, Pipeline, prompt_job, Message, tool
   ```

2. Set up your LLM context:

   ```python
   context = LLMContext(model=your_model, api_key=your_api_key)
   ```

3. Create a custom tool:

   ```python
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

4. Define prompt jobs:

   ```python
   @prompt_job(id="weather_query", context=context)
   def WeatherQueryJob(id: str, context: LLMContext, prevResult: Any):
       location = "New York"
       weather = get_weather(location)
       return (context.Prompt(Message("user", f"Describe the weather in {location}: {weather}"))
               .Run(stream=True)
               .Messages[-1])

   @prompt_job(id="summarize", context=context)
   def SummarizeJob(id: str, context: LLMContext, prevResult: Any):
       return (context.Prompt(Message("user", f"Summarize this weather description: {prevResult.Content}"))
               .Run(stream=True))
   ```

5. Create and run a pipeline:

   ```python
   pipeline = Pipeline(context)
   result = (pipeline.AddJob(WeatherQueryJob)
                     .AddJob(SummarizeJob)
                     .Run())
   print(result)
   ```

This basic example demonstrates how to use TinyTune to create a simple workflow that gets weather information, processes it through an LLM, and then summarizes the result.

## Next Steps

To dive deeper into TinyTune's capabilities, explore the following topics:

- [Core Concepts](core-concepts/)
- [Advanced Usage](advanced-usage/)
- [Best Practices](best-practices.md)

For a complete API reference, check the [API Documentation](api-reference/).
