---
layout: default
title: Dynamic Pipeline Construction
---

# Dynamic Pipeline Construction

TinyTune allows for dynamic construction of pipelines, enabling you to create flexible workflows that adapt to different conditions or inputs.

## Basic Dynamic Pipeline

```python
def construct_pipeline(context, condition):
    pipeline = Pipeline(context)
    pipeline.AddJob(Job1)

    if condition:
        pipeline.AddJob(Job2)
    else:
        pipeline.AddJob(Job3)

    pipeline.AddJob(Job4)
    return pipeline

result = construct_pipeline(context, some_condition).Run()
```

## Advanced Dynamic Pipeline Techniques

### 1. Job Factory Functions

Create jobs dynamically based on input:

```python
def create_translation_job(source_lang, target_lang):
    @prompt_job(id=f"translate_{source_lang}_to_{target_lang}", context=translation_context)
    def TranslationJob(id: str, context: LLMContext, prevResult: Any):
        text = prevResult.Content if prevResult else "Hello, world!"
        return context.Prompt(Message("user", f"Translate from {source_lang} to {target_lang}: {text}")).Run().Messages[-1]
    return TranslationJob

pipeline = Pipeline(context)
pipeline.AddJob(create_translation_job("en", "fr"))
pipeline.AddJob(create_translation_job("fr", "de"))
```

### 2. Conditional Branching

Implement more complex decision-making in your pipeline:

```python
def analyze_sentiment(text):
    # Implement sentiment analysis
    return "positive" if "good" in text.lower() else "negative"

@prompt_job(id="sentiment_branch", context=context)
def SentimentBranchJob(id: str, context: LLMContext, prevResult: Any):
    sentiment = analyze_sentiment(prevResult.Content)
    if sentiment == "positive":
        return context.Prompt(Message("user", "Expand on the positive aspects")).Run().Messages[-1]
    else:
        return context.Prompt(Message("user", "Suggest improvements")).Run().Messages[-1]

pipeline = Pipeline(context)
pipeline.AddJob(InitialJob)
pipeline.AddJob(SentimentBranchJob)
```

### 3. Loop-Based Job Addition

Add jobs to the pipeline based on a loop:

```python
def create_multi_step_pipeline(context, steps):
    pipeline = Pipeline(context)
    for i, step in enumerate(steps):
        @prompt_job(id=f"step_{i}", context=context)
        def StepJob(id: str, context: LLMContext, prevResult: Any, current_step=step):
            return context.Prompt(Message("user", f"Perform this step: {current_step}")).Run().Messages[-1]
        pipeline.AddJob(StepJob)
    return pipeline

steps = ["Research", "Outline", "Draft", "Edit", "Finalize"]
result = create_multi_step_pipeline(context, steps).Run()
```

### 4. Dynamic Tool Selection

Select and use different tools based on the input:

```python
tools = {
    "weather": WeatherTool(),
    "database": DatabaseTool(),
    "calculator": CalculatorTool()
}

@prompt_job(id="dynamic_tool_job", context=context)
def DynamicToolJob(id: str, context: LLMContext, prevResult: Any):
    tool_name = determine_required_tool(prevResult.Content)
    if tool_name in tools:
        tool_result = tools[tool_name].main_method(prevResult.Content)
        return context.Prompt(Message("user", f"Process this tool result: {tool_result}")).Run().Messages[-1]
    else:
        return context.Prompt(Message("user", "I don't have the required tool for this task.")).Run().Messages[-1]

pipeline = Pipeline(context)
pipeline.AddJob(InputAnalysisJob)
pipeline.AddJob(DynamicToolJob)
```

## Best Practices for Dynamic Pipelines

1. Ensure that dynamically created jobs have unique and descriptive IDs.
2. Handle potential errors that may occur due to dynamic construction.
3. Document the expected input and output of dynamically created jobs.
4. Use type hints and docstrings in factory functions to maintain clarity.
5. Consider implementing a validation step to ensure the dynamically constructed pipeline is valid before running it.

By leveraging these dynamic pipeline construction techniques, you can create highly flexible and adaptable workflows in TinyTune, capable of handling a wide range of scenarios and inputs.
