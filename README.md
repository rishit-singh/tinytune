# TinyTune 

TinyTune is a lightweight library designed for prompt tuning, enabling the use of Python functions as prompt sequences within an LLM-agnostic pipeline.

## Usage Guide
### Prompt Jobs
Prompt jobs are functions designed to execute user-defined prompts on the specified LLM (Language Model) and enable performing logic on the results. This functionality is crucial for orchestrating complex interactions with the language model, such as querying information or generating responses based on input prompts. By defining prompt jobs, users can encapsulate specific tasks or actions within their pipeline, facilitating modular and organized development of prompt-based workflows.

### Defining Prompt Jobs
Define prompt jobs using the `@prompt_job` decorator.
```python
llmContext = LLMContext() 

@prompt_job(id="search", context=llmContext)
def Job(id: str, context: LLMContext, prevResult: Any):
    (context.Prompt(Message("user", "Do XYZ"))
            .Run(stream=True))
    return context.Messages[-1]
```

### Pipelines
A pipeline is a managed container that maintains a queue of prompt jobs and runs them in a loop, one after another. The results of the current job are passed down to the next one in the queue, facilitating the sequential execution of tasks within the pipeline.

### Defining Pipeline
Create a pipeline and add prompt jobs to it.

```python
pipeline: Pipeline = Pipeline(context)
(pipeline.AddJob(Job)
        .AddJob(Job1))  # Job, and Job1 are prompt jobs, add more jobs if necessary
```

## Example

This example demonstrates the usage of the TinyTune library to orchestrate interactions with language models. It sets up two prompt jobs: one for searching for Indian restaurants in Vancouver using a PerplexityContext, and another for extracting data into JSON format using a GPTContext. These prompt jobs are then added to a pipeline, which executes them sequentially. The program showcases how to define prompt jobs, configure contexts, create pipelines, and run them to perform specific tasks such as searching for information and extracting data.

```python
# Initializing contexts
context = GPTContext("gpt-4-0125-preview", str(os.getenv("OPENAI_KEY")))
pContext = PerplexityContext("pplx-70b-online", os.getenv("PERPLEXITY_KEY"))

# Callback function
def Callback(content):
    if (content != None):
        print(content, end="")
    else:   
        print()

context.OnGenerateCallback = Callback
pContext.OnGenerateCallback = Callback

# Define prompt job for searching
@prompt_job(id="search", context=pContext)
def Job(id: str, context: PerplexityContext, prevResult: Any):
    (context.Prompt(PerplexityMessage("user", "Find me Japanese restaurants in Vancouver"))
            .Run(stream=True))

    return context.Messages[-1]

# Define prompt job for extracting JSON
@prompt_job("extract json", context)
def Job1(id: str, context: GPTContext, prevResult: Any):
    print("prevResult: ", prevResult.ToDict())
    (context.Prompt(GPTMessage("user", f"""{prevResult.Content} extract this data into JSON, and only return the JSON, no formatting, backticks, or explanation"""))
            .Run(stream=True)) 

# Create pipeline
pipeline: Pipeline = Pipeline(context)

# Add prompt jobs to the pipeline
(pipeline.AddJob(Job)
        .AddJob(Job1))

# Run the pipeline
pipeline.Run()
```
```