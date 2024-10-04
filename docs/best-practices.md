---
layout: default
title: Best Practices
---

# Best Practices

Following these best practices will help you use TinyTune effectively and create robust, maintainable LLM workflows.

## 1. Design Clear and Focused Prompt Jobs

- Keep each prompt job focused on a single task or concept.
- Use meaningful names and IDs for your prompt jobs.
- Include clear docstrings explaining the purpose and expected inputs/outputs of each job.

```python
@prompt_job(id="summarize_article", context=context)
def SummarizeArticleJob(id: str, context: LLMContext, prevResult: Any):
    """
    Summarizes an article provided in the prevResult.

    Args:
        id (str): Job ID.
        context (LLMContext): The LLM context.
        prevResult (Any): Expected to contain the article text.

    Returns:
        The last message from the LLM containing the summary.
    """
    return (context.Prompt(Message("user", f"Summarize this article in 3 sentences:\n\n{prevResult.Content}"))
            .Run(stream=True)
            .Messages[-1])
```

## 2. Leverage Tools for Complex Operations

- Use tools for operations that are beyond the LLM's capabilities or require external data.
- Create reusable tools that can be shared across different prompt jobs and pipelines.

```python
@tool
def fetch_stock_price(symbol: str):
    """
    Fetches the current stock price for a given symbol.

    Args:
        symbol (str): The stock symbol (e.g., "AAPL" for Apple Inc.)

    Returns:
        float: The current stock price.
    """
    # Implementation to fetch stock price
    return 150.75  # Example return value
```

## 3. Implement Proper Error Handling

- Use try-except blocks in your prompt jobs and tools to handle potential errors gracefully.
- Provide informative error messages that can help in debugging.

```python
@prompt_job(id="analyze_stock", context=context)
def AnalyzeStockJob(id: str, context: LLMContext, prevResult: Any):
    try:
        symbol = prevResult.Content.strip().upper()
        price = fetch_stock_price(symbol)
        return (context.Prompt(Message("user", f"Analyze the stock {symbol} with current price ${price:.2f}"))
                .Run(stream=True)
                .Messages[-1])
    except Exception as e:
        return context.Prompt(Message("user", f"An error occurred while analyzing the stock: {str(e)}")).Run().Messages[-1]
```

## 4. Use Type Hints and Docstrings

- Utilize type hints to improve code readability and catch potential type-related errors.
- Write comprehensive docstrings for your functions, classes, and methods.

```python
from typing import List, Dict

@tool
def analyze_sentiment(texts: List[str]) -> List[Dict[str, float]]:
    """
    Analyzes the sentiment of a list of texts.

    Args:
        texts (List[str]): A list of texts to analyze.

    Returns:
        List[Dict[str, float]]: A list of dictionaries, each containing 'positive' and 'negative' sentiment scores.
    """
    # Implementation
    return [{"positive": 0.8, "negative": 0.2} for _ in texts]
```

## 5. Optimize for Performance

- Use streaming responses when appropriate to reduce latency.
- Implement caching mechanisms for expensive operations or frequent API calls.
- Consider batching operations when dealing with large datasets.

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_calculation(input_data: str) -> float:
    # Expensive calculation here
    return result
```

## 6. Maintain Consistency Across Contexts

- When using multiple LLM contexts, ensure consistent formatting and structure in messages passed between them.
- Use a common schema for data passed between different parts of your pipeline.

## 7. Version Control Your Prompts

- Store your prompts in version-controlled files or databases.
- Use templating systems for prompts that require dynamic content.

```python
SUMMARIZATION_PROMPT = """
Summarize the following text in {num_sentences} sentences:

{text}
"""

@prompt_job(id="flexible_summarize", context=context)
def FlexibleSummarizeJob(id: str, context: LLMContext, prevResult: Any):
    num_sentences = 3  # This could be dynamically determined
    prompt = SUMMARIZATION_PROMPT.format(num_sentences=num_sentences, text=prevResult.Content)
    return context.Prompt(Message("user", prompt)).Run().Messages[-1]
```

## 8. Implement Logging and Monitoring

- Use logging to track the flow of your pipelines and aid in debugging.
- Implement monitoring for critical metrics like response times and error rates.

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@prompt_job(id="logged_job", context=context)
def LoggedJob(id: str, context: LLMContext, prevResult: Any):
    logger.info(f"Starting job {id}")
    result = context.Prompt(Message("user", "Perform a task")).Run().Messages[-1]
    logger.info(f"Completed job {id}")
    return result
```

By following these best practices, you can create more efficient, maintainable, and robust TinyTune workflows.
