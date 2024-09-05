
import json
import sys
import inspect

sys.path.append("..")
sys.path.append("../src")

from examples import parser
from examples.yt import YouTubeDataAPI

import os
from typing_extensions import Any, Callable
from GroqContext import WebGroqContext, WebGroqMessage
from tinytune.llmcontext import LLMContext, Message
from tinytune.pipeline import Pipeline
from tinytune.prompt import prompt_job
from examples.parser import Parse

from dotenv import load_dotenv

load_dotenv()

def Callback(chunk):
    if (chunk):
        print(chunk, end="")

LLM = WebGroqContext(model="llama-3.1-70b-versatile", apiKey=str(os.getenv("GROQ_KEY")))

LLM.OnGenerateCallback = Callback

yt_api = YouTubeDataAPI(str(os.getenv("YT_KEY")))

def tool():
    def wrapper(func: Callable):
        spec = inspect.getfullargspec(func)

        doc = Parse(str(func.__doc__))

        return (func, {
            "name": func.__name__,
            "description": doc["title"],
            "parameters": {
                "type": "object",
                "properties": doc["params"]["Args"] if isinstance(["params"], dict) else [ { key: str(spec.annotations[key]) } for key in spec.annotations ]
            },
            "repr": func.__repr__()
        })

    return wrapper

@tool()
def GetVideos(query: str, max: int) -> str:
    """
    Gets the videos based on a query and max arguments

    Args:
        query - Search query
        max - Max search results
    """
    videos = yt_api.search_videos(query, max_results=max, order='relevance', video_duration='short')

    # Extract the video IDs
    video_ids = [video['videoId'] for video in videos]

    # Get the view counts for the videos
    video_details = yt_api.get_video_details(video_ids)

    # Sort the videos by view count (low to high)
    videos_sorted = sorted(videos, key=lambda video: video_details[video['videoId']], reverse=True)

    # Initialize an empty string to store all video details
    result = ""

    # Loop through each video and append its details to the result string
    for video in videos_sorted:
          view_count = video_details[video['videoId']]
          video_link = f"https://www.youtube.com/watch?v={video['videoId']}"
          video_details_string = (
              f"Title: {video['title']}\n"
              f"Video ID: {video['videoId']}\n"
              f"Channel: {video['channelTitle']}\n"
              f"Published At: {video['publishedAt']}\n"
              f"Views: {view_count}\n"
              f"Link: {video_link}\n"
              f"Description: {video['description']}\n\n"
          )
          result += video_details_string

    return result


class ToolManager:
    ToolMap: dict = {}
    # @staticmethod
    # def Register(func: Callable):
    #     tool: dict = GenerateTool(func)
    #     ToolManager.ToolMap[tool["name"]] = tool

    @staticmethod
    def Call(tool: dict):
        return

# Agent 1
def Classifier(context: LLMContext, videos: str) -> Pipeline:
    pipeline = Pipeline(context)

    @prompt_job(id="Setup", context=context)
    def Setup(id: str, context: LLMContext, prevResult: Any, *args):

        func, tool = GetVideos

        return (context.Prompt(WebGroqMessage("user", f"""
        You have access to the following functions:

        Use the function '{tool["name"]}' to '{tool["description"]}':
        {json.dumps(tool)}

        If you choose to call a function ONLY reply in the following format with no prefix or suffix:

        <function=example_function_name>{{\"example_name\": \"example_value\"}}</function>

        Reminder:
        - Function calls MUST follow the specified format, start with <function= and end with </function>
        - Required parameters MUST be specified
        - Only call one function at a time
        - Put the entire function call reply on one line
        - If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls
        """)).Run(stream=True)
        .Prompt(WebGroqMessage("user", "Find me a fun youtube video. Call the appropriate function"))
        .Run(stream=True))

        print(LLM.Messages)

    @prompt_job(id="Classify", context=context)
    def Classify(id: str, context: LLMContext, prevResult: Any, *args):
        return context.Prompt(WebGroqMessage("user", f"Here are the videos {videos}. Give me a classification using this JSON format {{ 'category1': [ video1, video2 ], 'category':  [ video3, video4 ] }}")).Run(stream=True)

    @prompt_job(id="Extract", context=context)
    def Extract(id: str, context: LLMContext, prevResult: Any, *args):
        return context.Prompt(WebGroqMessage("user", f"{prevResult} extract just the json from this, respond with plain JSON text, no backticks, nothing extra.")).Run(stream=True).Messages[-1].Content

    return pipeline.AddJob(Setup)

# Agent 2
def Analyzer(context: LLMContext) -> Pipeline:
    pipeline = Pipeline(context)

    @prompt_job(id="Analyze", context=context)
    def Analyze(id: str, context: LLMContext, prevResult: Any, *args):
        return context.Prompt(WebGroqMessage("user", "Generate an analysis based on the video data you've given")).Run(stream=True).Messages[-1].Content

    @prompt_job(id="Analyze", context=context)
    def Plot(id: str, context: LLMContext, prevResult: Any, *args):
        return context.Prompt(WebGroqMessage("user", "Generate python3 code to plot this info in a 3D chart, return with just plain python code, no backticks, nothing extra.")).Run(stream=True).Messages[-1].Content

    return pipeline.AddJob(Analyze).AddJob(Plot)


Classifier(LLM, "")()
print('\n', LLM.Messages[-1].Content)
# with open("plot.py", 'w') as fp:
#     pipeline = Pipeline(LLM)

#     results = (pipeline.AddJob(Classifier(LLM, GetVideos("AI alignment", 155555)))
#                         .AddJob(Analyzer(LLM))
#                         .Run(stream=True))

#     fp.write(str(results))

def Foo(x: int, y: str, z: float):
    pass
    """
    A random function.

    Args:
        x - some int
        y - some string
        z - some float
    """

# print(GetVideosTool)
