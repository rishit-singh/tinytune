# TinyTune

TinyTune is a lightweight, flexible library designed for prompt tuning and orchestrating complex interactions with Language Models (LLMs). It enables the use of Python functions as prompt sequences within an LLM-agnostic pipeline, allowing for modular and organized development of prompt-based workflows.

## Key Features

- **LLM-agnostic**: Works with various Language Model contexts (e.g., GPT, Perplexity)
- **Prompt Jobs**: Encapsulate specific tasks or actions within the pipeline
- **Pipelines**: Manage and execute sequences of prompt jobs
- **Flexible Context Management**: Handle different types of LLM contexts
- **Tool Integration**: Easily convert functions into callable tools for language models

## Core Components

### LLMContext

The `LLMContext` class represents a context for a language model. It manages messages, a message queue, and callbacks.

Key methods:

- `Prompt`: Adds a message to the queue
- `Run`: Executes the model on the queued messages
- `Save`: Saves messages to a JSON file

### Prompt Jobs

Prompt jobs are functions designed to execute user-defined prompts on the specified LLM and enable performing logic on the results. They are crucial for orchestrating complex interactions with the language model.

#### Defining Prompt Jobs

Use the `@prompt_job` decorator to define prompt jobs:

```python
llmContext = LLMContext()

@prompt_job(id="search", context=llmContext)
def Job(id: str, context: LLMContext, prevResult: Any):
    return (context.Prompt(Message("user", "Do XYZ"))
            .Run(stream=True)
            .Messages[-1])
```

### Pipelines

A pipeline is a managed container that maintains a queue of prompt jobs and runs them in sequence. The results of each job are passed to the next one in the queue.

#### Defining Pipelines

Create a pipeline and add prompt jobs to it:

```python
pipeline: Pipeline = Pipeline(context)
(pipeline.AddJob(Job)
        .AddJob(Job1))  # Job and Job1 are prompt jobs
```

### Tools

Tools in TinyTune are functions decorated with the `@tool` decorator. This decorator extracts metadata from the function's docstring, making it easier to integrate custom functions into your LLM workflows. Tools can be used to extend the capabilities of your language model by allowing it to perform specific actions or retrieve information.

#### Creating a Tool

To create a tool, use the `@tool` decorator on a function:

```python
from tinytune.tool import tool

@tool
def search_videos(query, max_results=5, order="relevance"):
    """
    Searches for videos based on the given query and parameters.
    Args:
        query (str): The search query.
        max_results (int): Maximum number of results to return.
        order (str): The order of the search results.
    Returns:
        list: A list of dictionaries containing video information.
    """
    # Implementation here
```

#### Example: YouTube Data API Tool

Here's an example of a more complex tool that interacts with the YouTube Data API:

```python
import os
from googleapiclient.discovery import build
from tinytune.tool import tool

class YouTubeDataAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    @tool
    def search_videos(self, query, max_results=5, order="relevance", video_duration="any", video_type="any"):
        """
        Searches for videos based on the given query and parameters.
        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.
            order (str): The order of the search results.
            video_duration (str): Duration of the videos to search for.
            video_type (str): Type of videos to search for.
        Returns:
            list: A list of dictionaries containing video information.
        """
        request = self.youtube.search().list(
            q=query,
            part="snippet",
            maxResults=max_results,
            order=order,
            type="video",
            videoDuration=video_duration,
            videoType=video_type,
        )
        response = request.execute()

        videos = []
        for item in response.get("items", []):
            video_info = {
                "videoId": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "channelTitle": item["snippet"]["channelTitle"],
                "publishedAt": item["snippet"]["publishedAt"],
            }
            videos.append(video_info)

        return videos

    # Additional methods (get_video_details, get_channel_info, etc.) can be added here

    def get_function_map(self):
        """
        Returns a dictionary mapping function names to their references.
        """
        return {name: func for name, func in vars(self.__class__).items() if isinstance(func, tuple)}

    def call_method(self, function_call):
        """
        Calls a method based on the provided function call structure.
        """
        function_name = function_call.get("function")
        params = function_call.get("params", {})
        params["self"] = self

        function_map = self.get_function_map()

        if function_name not in function_map:
            raise ValueError(f"Function '{function_name}' not found")

        try:
            return function_map[function_name][0](**params)
        except Exception as e:
            raise ValueError(f"Error calling function '{function_name}': {str(e)}")
```

This YouTube Data API tool demonstrates how to create a more complex tool with multiple methods, each decorated with `@tool`. The `get_function_map` and `call_method` functions allow for dynamic method calling, which can be useful when integrating with language models.

## Using Tools in Prompt Jobs

You can use tools within prompt jobs to extend the capabilities of your language model. Here's an example of how to integrate a tool into a prompt job:

```python
yt_api = YouTubeDataAPI(api_key)

@prompt_job(id="search_videos", context=llmContext)
def SearchVideos(id: str, context: LLMContext, prevResult: Any, query: str):
    videos = yt_api.search_videos(query, max_results=5)
    response = context.Prompt(Message("user", f"Summarize these video results: {videos}"))
    return response.Run(stream=True).Messages[-1]
```

## Example Workflow

This example demonstrates how to use TinyTune to orchestrate interactions with different language models and integrate custom tools:

```python
import os
from tinytune import GPTContext, PerplexityContext, Pipeline, prompt_job, Message
from youtube_tool import YouTubeDataAPI

# Initialize contexts and tools
context = GPTContext("gpt-4-0125-preview", os.getenv("OPENAI_KEY"))
pContext = PerplexityContext("pplx-70b-online", os.getenv("PERPLEXITY_KEY"))
yt_api = YouTubeDataAPI(os.getenv("YOUTUBE_API_KEY"))

# Callback function for printing output
def Callback(content):
    print(content, end="" if content else "\n")

context.OnGenerateCallback = Callback
pContext.OnGenerateCallback = Callback

# Define prompt job for searching YouTube videos
@prompt_job(id="search_videos", context=pContext)
def SearchVideos(id: str, context: PerplexityContext, prevResult: Any):
    query = "Latest AI developments"
    videos = yt_api.search_videos(query, max_results=5)
    return (context.Prompt(Message("user", f"Summarize these AI video results: {videos}"))
            .Run(stream=True)
            .Messages[-1])

# Define prompt job for generating a report
@prompt_job("generate_report", context)
def GenerateReport(id: str, context: GPTContext, prevResult: Any):
    return (context.Prompt(Message("user", f"Generate a brief report on the latest AI developments based on this summary: {prevResult.Content}"))
            .Run(stream=True))

# Create and run pipeline
pipeline = Pipeline(context)
(pipeline.AddJob(SearchVideos)
        .AddJob(GenerateReport)
        .Run())
```

This example showcases how to:

1. Set up different LLM contexts (GPT and Perplexity)
2. Integrate a custom YouTube Data API tool
3. Define prompt jobs that use both LLM contexts and custom tools
4. Create a pipeline to search for videos, summarize results, and generate a report

## Getting Started

1. Install TinyTune: `pip install tinytune`
2. Import necessary components: `from tinytune import LLMContext, Pipeline, prompt_job, Message, tool`
3. Set up your LLM context(s)
4. Create custom tools using the `@tool` decorator
5. Define your prompt jobs using the `@prompt_job` decorator
6. Create a pipeline and add your jobs
7. Run the pipeline to execute your workflow

For more detailed information and advanced usage, please refer to the documentation.
