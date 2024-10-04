import json
from re import U
import sys
import inspect

sys.path.append("..")
sys.path.append("../src")

from examples import parser
from examples.yt import YouTubeDataAPI

import os
from typing_extensions import Any, Callable, Tuple
from GroqContext import WebGroqContext, WebGroqMessage
from tinytune.llmcontext import LLMContext, Message
from tinytune.pipeline import Pipeline
from tinytune.prompt import prompt_job
from examples.parser import Parse
from tinytune.tool import tool
from dotenv import load_dotenv

load_dotenv()


def Callback(content: Any):
    if content:
        print(content, end="")


LLM = WebGroqContext(model="llama-3.1-70b-versatile", apiKey=str(os.getenv("GROQ_KEY")))

LLM.OnGenerate = Callback

LLM1 = WebGroqContext(
    model="llama-3.1-70b-versatile", apiKey=str(os.getenv("GROQ_KEY"))
)

yt_api = YouTubeDataAPI(str(os.getenv("YT_KEY")))


@tool
def GetVideos(query: str, max: int) -> str:
    """
    Gets the videos based on a query and max arguments

    Args:
        query - Search query
        max - Max search results
    """
    videos = yt_api.search_videos(
        query, max_results=max, order="relevance", video_duration="short"
    )

    # Extract the video IDs
    video_ids = [video["videoId"] for video in videos]

    # Get the view counts for the videos
    video_details = yt_api.get_video_details(video_ids)

    # Sort the videos by view count (low to high)
    videos_sorted = sorted(
        videos, key=lambda video: video_details[video["videoId"]], reverse=True
    )

    # Initialize an empty string to store all video details
    result = ""

    # Loop through each video and append its details to the result string
    for video in videos_sorted:
        view_count = video_details[video["videoId"]]
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


FunctionMap = yt_api.get_function_map()


@tool
@prompt_job(id="Prompt", context=LLM1)
def Prompt(id, context, prevResult, input: str):
    return (
        context.Prompt(
            WebGroqMessage(
                "user",
                "You're Geohot, you only talk like him.",
            )
        )
        .Run(stream=True)
        .Prompt(WebGroqMessage("user", input))
        .Run(stream=True)
        .Messages[-1]
        .Content
    )


FunctionMap["Prompt"] = Prompt


@tool
@prompt_job("ExplainDescription", context=LLM1)
def DescriptionExplanation(id, context, prevResult, description: str):
    return (
        context.Prompt(
            WebGroqMessage(
                "user",
                "You are a Youtube expert. You acccept video descriptions and give out explanantions",
            )
        )
        .Prompt(WebGroqMessage("user", description))
        .Run(stream=True)
        .Messages[-1]
        .Content
    )


FunctionMap["ExplainDescription"] = DescriptionExplanation


def Chat(context: LLMContext):
    Running = True

    @prompt_job(id="Setup", context=context)
    def Setup(id: str, context: LLMContext, prevResult: Any, *args):
        return (
            context.Prompt(
                WebGroqMessage(
                    "user",
                    f"""
                        You have access to the following functions:

                        Use the following functions:
                        {json.dumps([ FunctionMap[key][1] for key in FunctionMap])}

                        If you choose to call a function ONLY reply in the following format with no prefix or suffix:

                        {{
                            "function": "function_name",
                            "params": {{
                                "param": "value"
                            }}
                        }}

                        Reminder:
                        - Function calls MUST follow the specified format.
                        - Required parameters MUST be specified
                        - Only call one function at a time
                        - Put the entire function call reply on one line
                        - If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls
                        - Never make responses bigger than one paragraph if you dont have a function to call.
                        - Make sure the params of the function call you return are the same as the ones specified.
                        """,
                )
            )
        ).Run(stream=True)

        # return GetVideos[0](func["params"]["query"], int(func["params"]["max"]))

    @prompt_job(id="UserPrompt", context=context)
    def UserPrompt(id: str, context: LLMContext, prevResult: Any, *args):
        inp = input("\n> ")

        if inp == "exit":
            Running = False
            return "exit"

        return (
            context.Prompt(
                WebGroqMessage(
                    "user", f"{inp}. Call the necessary functions where needed"
                )
            )
            .Run(stream=True)
            .Messages[-1]
            .Content
        )

    @prompt_job(id="Execute", context=context)
    def Execute(id: str, context: LLMContext, prevResult: Any, *args):
        func: dict = {}

        try:
            func: dict = json.loads(str(prevResult))

            resp = json.dumps(yt_api.call_method(func))

            context.Messages.append(WebGroqMessage("assistant", resp))

        except ValueError as e:
            function_name = func.get("function")

            if function_name == "Prompt":
                params = func.get("params", {})

                params.pop("self")

                result = FunctionMap[str(function_name)][0](**params)

                context.Messages.append(WebGroqMessage("assistant", result))

        except Exception as e:
            pass

    Setup()

    context.OnGenerate = Callback

    while Running:
        pipeline = Pipeline(llm=context)
        pipeline.AddJob(UserPrompt, "random").AddJob(Execute).Run(stream=True)


Chat(LLM)
