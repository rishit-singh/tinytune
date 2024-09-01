import json
import sys

sys.path.append("..")
sys.path.append("../src")

from examples.yt import YouTubeDataAPI

import os
from typing_extensions import Any
from GroqContext import WebGroqContext, WebGroqMessage
from tinytune.llmcontext import LLMContext, Message
from tinytune.pipeline import Pipeline
from tinytune.prompt import prompt_job

from dotenv import load_dotenv

load_dotenv()

def Callback(chunk):
    if (chunk):
        print(chunk, end="")

LLM = WebGroqContext(model="llama-3.1-70b-versatile", apiKey=str(os.getenv("GROQ_KEY")))

LLM.OnGenerateCallback = Callback

yt_api = YouTubeDataAPI(str(os.getenv("YT_KEY")))

def GetVideos(query: str, max: int) -> str:
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

# Agent 1
def Classifier(context: LLMContext, videos: str) -> Pipeline:
    pipeline = Pipeline(context)

    @prompt_job(id="Setup", context=context)
    def Setup(id: str, context: LLMContext, prevResult: Any, *args):
        return context.Prompt(WebGroqMessage("user", "You are a YT video analyzer. You take a list of youtube videos, stats, and descriptions, and group the similar ones together.")).Run(stream=True)

    @prompt_job(id="Classify", context=context)
    def Classify(id: str, context: LLMContext, prevResult: Any, *args):
        return context.Prompt(WebGroqMessage("user", f"Here are the videos {videos}. Give me a classification using this JSON format {{ 'category1': [ video1, video2 ], 'category':  [ video3, video4 ] }}")).Run(stream=True)

    @prompt_job(id="Extract", context=context)
    def Extract(id: str, context: LLMContext, prevResult: Any, *args):
        return context.Prompt(WebGroqMessage("user", f"{prevResult} extract just the json from this, respond with plain JSON text, no backticks, nothing extra.")).Run(stream=True).Messages[-1].Content

    return pipeline.AddJob(Setup).AddJob(Classify).AddJob(Extract)

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


with open("plot.py", 'w') as fp:
    pipeline = Pipeline(LLM)

    results = (pipeline.AddJob(Classifier(LLM, GetVideos("AI alignment", 155555)))
                        .AddJob(Analyzer(LLM))
                        .Run(stream=True))

    fp.write(str(results))
