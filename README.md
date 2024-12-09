# TinyTune

TinyTune is a lightweight, flexible library designed to make prompt engineering and workflow orchestration with Large Language Models (LLMs) more structured and manageable. It provides a simple, model-agnostic way to:

- Organize your LLM prompts into modular **prompt jobs**
- Chain these jobs together in **pipelines**
- Incorporate **tools**—simple Python functions callable by LLMs—to extend capabilities

**Why use TinyTune?**  
Instead of scattering prompt strings all over your code, TinyTune lets you maintain clarity and reusability. Prompt jobs are defined as functions, pipelines manage sequences of these jobs, and tools let you seamlessly integrate external functionalities.

# Getting Started

## Installation

Install TinyTune via pip:

```bash
pip install tinytune
```

## Key Concepts

### LLMContext
**LLMContext** is your interface to a language model. It handles sending messages to the model and receiving responses. You can use different backends (e.g., GPT, other APIs) without changing the rest of your code.

Example:
```python
from tinytune.contexts import GPTContext

# Initialize a GPTContext with your model name and API key
context = GPTContext("o1-mini", "YOUR_OPENAI_API_KEY")
```

### Prompt Jobs
A **prompt job** is a function that:
- Takes a context and an optional previous result.
- Sends one or more messages to the LLM.
- Returns the LLM’s response.

You define a prompt job using the `@prompt_job` decorator. The `id` parameter uniquely identifies the job, and `context` specifies which LLM context it uses.

Example:

```python
from tinytune import prompt_job, Message, LLMContext

@prompt_job(id="summarize", context=context)
def SummarizeJob(id: str, context: LLMContext, prevResult: any):
    return (context
            .Prompt(Message("user", "Summarize the latest AI trends"))
            .Run(stream=True)
            .Messages[-1])
```

### Pipelines
A **pipeline** chains multiple prompt jobs together. The output of each job is passed as `prevResult` to the next job, allowing you to build complex workflows step-by-step.

Example:
```python
from tinytune import Pipeline

pipeline = Pipeline(context)
pipeline.AddJob(SummarizeJob)

result = pipeline.Run()
print(result.Content)
```

This pipeline runs the `SummarizeJob` and prints the model’s summarized response.

### Tools
A **tool** is a Python function that the LLM can invoke as part of your prompt jobs. Tools let you integrate external data or functionality into your LLM workflows. By decorating a Python function with `@tool`, you provide metadata that TinyTune can use to incorporate it into prompts and pipelines easily.

For example, let’s create a simple tool that returns the current date. While this is a trivial tool, it illustrates the concept. In a real scenario, you could integrate APIs or complex logic.

```python
from tinytune.tool import tool
from datetime import date

@tool
def get_current_date():
    """
    Returns the current date as a string.
    Returns:
        str: The current date in YYYY-MM-DD format.
    """
    return date.today().isoformat()
```

You can now use this tool within a prompt job, like so:

```python
@prompt_job(id="date_summary", context=context)
def DateSummaryJob(id: str, context: LLMContext, prevResult: any):
    # Call the tool directly in Python:
    today = get_current_date()
    
    # Use the tool's result in your prompt
    return (context
            .Prompt(Message("user", f"Given that today's date is {today}, summarize today's world news."))
            .Run(stream=True)
            .Messages[-1])
```

Then, in your pipeline:
```python
pipeline = Pipeline(context)
pipeline.AddJob(DateSummaryJob)

result = pipeline.Run()
print(result.Content)
```

The LLM will see the current date in its prompt and can incorporate that into its response.

## Putting It All Together

Here’s a minimal end-to-end example:

```python
import os
from tinytune import GPTContext, Pipeline, prompt_job, Message
from tinytune.tool import tool
from datetime import date

# 1. Create the LLM context
context = GPTContext("o1-mini", os.getenv("OPENAI_API_KEY"))

# 2. Create a simple tool
@tool
def get_current_date():
    """
    Returns today's date in YYYY-MM-DD format.
    """
    return date.today().isoformat()

# 3. Define a prompt job that uses the tool
@prompt_job(id="date_summarize", context=context)
def DateSummarize(id: str, context: GPTContext, prevResult: any):
    today = get_current_date()
    return (context
            .Prompt(Message("user", f"Today's date is {today}. Please summarize the main tech headlines."))
            .Run(stream=True)
            .Messages[-1])

# 4. Create and run the pipeline
pipeline = Pipeline(context)
pipeline.AddJob(DateSummarize)

final_result = pipeline.Run()
print(final_result.Content)  # Print the summary of today's tech headlines
```
## Function Calling

Tools can be used with function calling by providing this system prompt:

```
You can call functions by responding with JSON:
{
    "function": "function_name",
    "params": {
        "param1": "value1"
    }
}

Available functions:
- get_weather(location: str): Gets current weather
- search_data(query: str): Searches database
```

## Key Classes & Decorators

- **LLMContext**: Interface to a language model (prompting, running, saving messages).
- **@prompt_job**: Decorates a function to define a prompt job.
- **Pipeline**: Manages and executes a sequence of prompt jobs.
- **@tool**: Converts a Python function into a callable tool for LLMs.


## Advanced Usage

- Integrate multiple different LLM contexts (e.g., GPT for reasoning and another model for specialized tasks).
- Add more complex tools (e.g., calling web APIs, databases, search engines).
- Implement function calling, callbacks, and streaming to enhance interactivity and responsiveness.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

TinyTune is licensed under the MIT License.