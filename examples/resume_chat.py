import json
import os
import sys
from typing import Any

sys.path.append("..")
sys.path.append("../src")

from examples.GroqContext import WebGroqContext, WebGroqMessage
from tinytune.llmcontext import LLMContext, Message
from tinytune.pipeline import Pipeline
from tinytune.prompt import prompt_job
from dotenv import load_dotenv

import PyPDF2

load_dotenv()

# Load LLM context
LLM = WebGroqContext(model="llama-3.1-70b-versatile", apiKey=str(os.getenv("GROQ_KEY")))


def print_callback(chunk):
    if chunk:
        print(chunk, end="")


def extract_pdf_text(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text


# This is where the extracted resume text will be stored
resume_text = extract_pdf_text(sys.argv[1])


# Set up the personality by giving the context the resume content
def ChatWithResume(context: LLMContext):
    Running = True

    context.OnGenerateCallback = print_callback

    @prompt_job(id="Setup", context=context)
    def Setup(id: str, context: LLMContext, prevResult: Any, *args):
        message = WebGroqMessage(
            "user",
            f"""
            You are now the candidate whose resume is as follows:

            {resume_text}

            You will answer questions as if you are this person.
            Answer questions based on the information provided in the resume.
            Be concise, factual, and accurate. If you don’t know something, say so.
            """,
        )

        return context.Prompt(message).Run(stream=True)

    @prompt_job(id="UserPrompt", context=context)
    def UserPrompt(id: str, context: LLMContext, prevResult: Any, *args):
        inp = input("\n> ")

        if inp.lower() == "exit":
            nonlocal Running
            Running = False
            return "exit"

        return (
            context.Prompt(
                WebGroqMessage(
                    "user", f"{inp}. Answer as if you are the person from the resume."
                )
            )
            .Run(stream=True)
            .Messages[-1]
            .Content
        )

    Setup()

    while Running:
        pipeline = Pipeline(llm=context)
        pipeline.AddJob(UserPrompt).Run(stream=True)


# Start chatting with the resume content
ChatWithResume(LLM)
