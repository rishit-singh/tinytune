from logging import WARN
from typing import Callable, Any
from dataclasses import dataclass
import json

class Message:
    """
    Represents a message with a role and content.
    """
    __slots__ = ("Role", "Content")

    def __init__(self, role: str, content: str):
        """
        Initialize a Message object.

        Parameters:
        - role (str): The role of the message.
        - content (str): The content of the message.
        """
        self.Role = role
        self.Content = content

    def ToDict(self):
        """
        Convert the message to a dictionary.

        Returns:
        - dict: A dictionary representation of the message.
        """
        return {
            "role": self.Role,
            "content": self.Content
        }

class Model:
    """
    Represents a model with an owner and name.
    """
    def __init__(self, owner: str, name: str):
        """
        Initialize a Model object.

        Parameters:
        - owner (str): The owner of the model.
        - name (str): The name of the model.
        """
        self.Owner: str = owner
        self.Name: str = name


class LLMContext[MessageType]:
    """
    Represents a context for a language model with support for a specific message type.
    """
    def __init__(self, model: Model):
        """
        Initialize an LLMContext object.

        Parameters:
        - model (Model): The model associated with the context.
        """
        self.Messages: list[MessageType] = []
        self.MessageQueue: list[MessageType] = []
        self.Model: Model = model
        self.QueuePointer: int = 0
        self.CallbackStack: dict[int, list[Callable]] = {}


    def Top(self) -> MessageType:
        """
        Get the top message in the context stack
        Returns:
        - MessageType: The top message in the context stack.
        """
        return self.Messages[len(self.Messages) - 1]

    def Prompt(self, message: MessageType) -> Any:
        """
        Add a message to the message queue.

        Parameters:
        - message (MessageType): The message to add to the queue.

        Returns:
        - Any: The LLMContext object.
        """
        self.MessageQueue.append(message)
        return self

    def Save(self, promptFile: str = "prompts.json") -> Any:
        """
        Save the messages in the context to a JSON file.

        Parameters:
        - promptFile (str): The file path to save the messages to.

        Returns:
        - Any: The LLMContext object.
        """
        try:
            with open(promptFile, "w") as fp:
                json.dump([ message.ToDict() for message in self.Messages ], fp, indent=2)

        except Exception as e:
            print(f"An error occurred in saving messages: {e.args[0]}")
            return self

    def Then(self, callback: Callable):
        key = len(self.MessageQueue) - 1

        if key in self.CallbackStack:
            self.CallbackStack[len(self.MessageQueue) - 1].append(callback)

        else:
            self.CallbackStack[key] = [ callback ]

        return self

    def OnGenerate(self, content: Any):
        return

    def OnRun(self, *args, **kwargs) -> Any:

        return

    def Run(self, *args, **kwargs):
        """
        Placeholder method for running the model.

        Returns:
        - Any: Result of running the model.
        """
        while self.QueuePointer < len(self.MessageQueue):
            self.Messages.append(self.MessageQueue[self.QueuePointer])

            result = self.OnRun(args, kwargs)

            callbacks = self.CallbackStack.get(self.QueuePointer)

            if callbacks:
                result = self.Messages[-1]

                for callback in callbacks:
                    result = callback(self, result)
                self.CallbackStack.pop(self.QueuePointer)

            self.Messages.append(result)
            self.QueuePointer += 1

        return self
