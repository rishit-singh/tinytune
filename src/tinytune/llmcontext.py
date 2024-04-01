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
        self.OnGenerateCallback: Callable[[list[str]], None] = lambda tokens : None 

    def Top(self) -> MessageType:
        """
        Get the top message in the context stack.

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

        return self

    def Run(self, *args, **kwargs):   
        """
        Placeholder method for running the model.

        Returns:
        - Any: Result of running the model.
        """
        return self
