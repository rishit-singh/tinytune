---
layout: default
title: LLM Context
---

# LLM Context

The `LLMContext` class is a fundamental component of TinyTune, representing the context for interacting with a language model.

## Overview

`LLMContext` manages messages, a message queue, and callbacks for a specific language model. It provides methods to add prompts, run the model, and save the conversation history.

## Key Methods

### Initialization

```python
context = LLMContext(model=your_model)
```

### Adding a Prompt

```python
context.Prompt(Message("user", "Hello, world!"))
```

### Running the Model

```python
response = context.Run(stream=False)
```

### Saving the Conversation

```python
context.Save(promptFile="conversation.json")
```

## Example Usage

```python
from tinytune import LLMContext, Message

# Initialize the context
context = LLMContext(model=your_model)

# Add a prompt
context.Prompt(Message("user", "What is the capital of France?"))

# Run the model
response = context.Run()

# Print the response
print(response.Messages[-1].Content)

# Save the conversation
context.Save("france_capital_query.json")
```

## Advanced Features

- **Streaming**: Use `Run(stream=True)` for real-time responses.
- **Callbacks**: Set `OnGenerate` callback for custom handling of generated content.

For more details, see the [LLMContext API Reference](../api-reference/llm-context.md).
