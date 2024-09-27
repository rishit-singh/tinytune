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


class ToolManager:
    ToolMap: dict = {}

    @staticmethod
    def Call(tool: dict):
        return


FunctionMap = yt_api.get_function_map()


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
        try:
            func: dict = json.loads(str(prevResult))

            print("Response: ", func)

            resp = json.dumps(yt_api.call_method(func))

            print(resp)

            context.Messages.append(WebGroqMessage("assistant", resp))
        except Exception as e:
            # print(e)'
            pass

    Setup()

    context.OnGenerate = Callback

    while Running:
        pipeline = Pipeline(llm=context)
        pipeline.AddJob(UserPrompt).AddJob(Execute).Run(stream=True)


# Agent 2
def Analyze(context: LLMContext) -> Pipeline:
    pipeline = Pipeline(context)

    @prompt_job(id="Analyze", context=context)
    def Analyze(id: str, context: LLMContext, prevResult: Any, *args):
        return (
            context.Prompt(
                WebGroqMessage(
                    "user", "Generate an analysis based on the video data you've given"
                )
            )
            .Run(stream=True)
            .Then(lambda _, message: json.loads(message.Content))
            .Messges[-1]
            .Content
        )

    @prompt_job(id="Analyze", context=context)
    def Plot(id: str, context: LLMContext, prevResult: Any, *args):
        return (
            context.Prompt(
                WebGroqMessage(
                    "user",
                    "Generate python3 code to plot this info in a 3D chart, return with just plain python code, no backticks, nothing extra.",
                )
            )
            .Run(stream=True)
            .Messages[-1]
            .Content
        )

    return pipeline.AddJob(Analyze).AddJob(Plot)

@prompt_job(id="basic", context=LLM)
def Prompt(id, context, prevResult, *args):
    try:
        context.Prompt(
            WebGroqMessage(
                "user",
                "You're a JSON API. You always respond in JSON. No backticks, no explaination, just plain JSON text.",
            )
        ).Then(lambda _, message: json.loads(message.Content)).Then(
            lambda _, message: print("\n", message)
        ).Run(
            stream=True
        )
    except Exception as e:
        print(e)
        Prompt()

@prompt_job(id="WriteTenDrafts")
def write_ten_drafts(id: str, context: WebGroqContext, prevResult: str, idea: str):
    print()

    return context.Prompt(WebGroqMessage("user", f"Write a story about {idea}. The story should only be 3 paragraphs.")).Run(stream=True).Messages[-1].Content

@prompt_job(id="ChooseBestDraft")
def choose_the_best_draft(id: str, context: WebGroqContext, prevResult: list[str]):
    return context.Prompt(WebGroqMessage("user", f"Choose the best draft from the following list:\n {'\n'.join(prevResult)}.")).Run(stream=True).Messages[-1].Content

Pipeline(LLM).AddJob(write_ten_drafts, idea="Elon Musk and Mark Zuckerberg").AddJob(choose_the_best_draft).Run(stream=True)

#  Classifier(LLM, sys.argv[1])()
# print(pipe
# print('\n', LLM.Messages[-1].Content)
# with open("plot.py", 'w') as fp:
#     pipeline = Pipeline(LLM)

#     results = (pipeline.AddJob(Classifier(LLM, GetVideos("AI alignment", 155555))):
#                         .AddJob(Analyzer(LLM))
#                         .Run(stream=True))

#     fp.write(str(results))

# Chat(LLM)
