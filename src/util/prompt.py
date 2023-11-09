RequiredPromptKeys: list = list([
    "role", "content"
])

def ValidatePrompt(prompt: dict[str, str]):
    keys: list = list(prompt.keys())

    for key in RequiredPromptKeys:
        if (not(key in keys)):
            raise KeyError(key)             
