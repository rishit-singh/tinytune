---
layout: default
title: LLMContext API Reference
---

# LLMContext API Reference

The `LLMContext` class represents the context for interacting with a language model.

## Class Definition

```python
class LLMContext[MessageType]:
    def __init__(self, model: Model):
        ...

    def Prompt(self, message: MessageType) -> Any:
        ...

    def Run(self, *args, **kwargs) -> Any:
        ...

    def Save(self, promptFile: str = "prompts.json") -> Any:
        ...

    def Top(self) -> MessageType:
        ...

    def OnGenerate(self, content: Any) -> None:
        ...
```

## Methods

### `__init__(self, model: Model)`

Initializes an LLMContext object.

**Parameters:**

- `model` (Model): The model associated with the context.

### `Prompt(self, message: MessageType) -> Any`

Adds a message to the message queue.

**Parameters:**

- `message` (MessageType): The message to add to the queue.

**Returns:**

- Any: The LLMContext object.

### `Run(self, *args, **kwargs) -> Any`

Executes the model on the queued messages.

**Parameters:**

- `*args`: Variable length argument list.
- `**kwargs`: Arbitrary keyword arguments.

**Returns:**

- Any: Result of running the model.

### `Save(self, promptFile: str = "prompts.json") -> Any`

Saves the messages in the context to a JSON file.

**Parameters:**

- `promptFile` (str, optional): The file path to save the messages to. Defaults to "prompts.json".

**Returns:**

- Any: The LLMContext object.

### `Top(self) -> MessageType`

Gets the top message in the context stack.

**Returns:**

- MessageType: The top message in the context stack.

### `OnGenerate(self, content: Any) -> None`

Callback method for handling generated content.

**Parameters:**

- `content` (Any): The generated content.

## Usage Example

```python
from tinytune import LLMContext, Message

context = LLMContext(model=your_model)

context.Prompt(Message("user", "What is the capital of France?"))
response = context.Run()

print(response.Messages[-1].Content)

context.Save("france_query.json")
```

For more detailed information and advanced usage, please refer to the [LLMContext documentation](../core-concepts/llm-context.md).
