---
layout: default
title: Working with Multiple Contexts
---

# Working with Multiple Contexts

TinyTune allows you to work with multiple LLM contexts in the same pipeline, enabling you to leverage different language models for specialized tasks.

## Creating Multiple Contexts

```python
from tinytune import GPTContext, PerplexityContext

context1 = GPTContext("gpt-4", api_key1)
context2 = PerplexityContext("pplx-70b", api_key2)
```

## Using Different Contexts in Prompt Jobs

```python
@prompt_job(id="job1", context=context1)
def Job1(id: str, context: LLMContext, prevResult: Any):
    return context.Prompt(Message("user", "Task for GPT-4")).Run().Messages[-1]

@prompt_job(id="job2", context=context2)
def Job2(id: str, context: LLMContext, prevResult: Any):
    return context.Prompt(Message("user", f"Task for Perplexity based on: {prevResult.Content}")).Run().Messages[-1]
```

## Creating a Multi-Context Pipeline

```python
pipeline = Pipeline(context1)  # The initial context doesn't matter much here
pipeline.AddJob(Job1).AddJob(Job2)
result = pipeline.Run()
```

## Best Practices

1. Use specialized models for specific tasks (e.g., GPT-4 for reasoning, a fine-tuned model for domain-specific tasks).
2. Be mindful of the differences in output format between different models.
3. Use a consistent message format (e.g., always use the last message from the previous job) when passing information between contexts.

## Example: Multi-Model Translation Pipeline

```python
en_to_fr_context = TranslationContext("en-fr-model", api_key1)
fr_to_de_context = TranslationContext("fr-de-model", api_key2)

@prompt_job(id="en_to_fr", context=en_to_fr_context)
def EnglishToFrench(id: str, context: LLMContext, prevResult: Any):
    text = "Hello, world!" if prevResult is None else prevResult.Content
    return context.Prompt(Message("user", f"Translate to French: {text}")).Run().Messages[-1]

@prompt_job(id="fr_to_de", context=fr_to_de_context)
def FrenchToGerman(id: str, context: LLMContext, prevResult: Any):
    return context.Prompt(Message("user", f"Translate to German: {prevResult.Content}")).Run().Messages[-1]

pipeline = Pipeline(en_to_fr_context)
pipeline.AddJob(EnglishToFrench).AddJob(FrenchToGerman)
result = pipeline.Run()
print(result.Content)  # Should be the German translation of "Hello, world!"
```

This example demonstrates how to create a translation pipeline that uses two different translation models in sequence.
