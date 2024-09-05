def Parse(docString: str) -> dict:
    doc = {
        "title": "",
        "params": {}
    }

    key = "title"

    innerKey = None

    docString = docString.replace("\n\n", "\n")

    for line in docString.split('\n'):
        line = line.strip()

        colon: int = line.find(':')

        if (line == '' or line == "\n"):
            continue

        if (colon >= 1):
            key = "params"

            innerKey = line[0 : colon]

            doc[key][innerKey] = ""

        elif (colon < 0):
            if (key == "title"):
                doc[key] += f"{line}\n"

            elif (key == "params"):
                hyphen = line.find('-')

                if (hyphen < 1):
                    print(key, innerKey, line)
                    doc[key][innerKey] += f"{line}\n"

                else:
                    paramKey = line[0 : hyphen].strip()

                    if (isinstance(doc[key][innerKey], dict)):
                        doc[key][innerKey][paramKey] = line[hyphen + 1:].strip()

                    else:
                        print(f"Setting: {key}, {innerKey}")
                        doc[key][innerKey] = { paramKey: line[hyphen + 1:].strip() }
    return doc

# print(Parse(
#         '''"""
#         Docstring with inconsistent section markers

#         Args:
#             Foo - Bar
#             Fizz - Buzz

#         Returns:
#             No colon after Returns

#         Raises:
#         No description for Raises
#         """'''))


docstring_edge_cases = [
    '"""Empty docstring"""',

    '"Single line docstring without triple quotes"',

    "'''Single line docstring with single quotes'''",

    '''"""
    Multiline docstring
    with irregular
      indentation
    """''',

    '''"""Docstring with special characters: \\n \\t \\r \\\\ "quoted text" 'single quotes'"""''',

    '''"""
    Docstring with inconsistent section markers

    Args:
        No actual args listed

    Returns
        No colon after Returns

    Raises:
    No description for Raises
    """''',

    '''"""Docstring with special characters: \\n \\t \\r \\\\ "quoted text" 'single quotes'"""''',

    '''"""
    Docstring with non-standard sections

    Input:
        x (int): An integer input

    Output:
        bool: A boolean output
    """''',

    '''"""Docstring with Unicode characters: áéíóú ñ 你好 😊"""''',

    '''"""
    Docstring with code blocks
<
    Example:
        >>> def example():
        ...     pass
        >>> example()
    """''',

    '''"""Docstring with multiple consecutive newlines


    Like this
    """''',

    '''"""
    Docstring with malformed type hints

    Args:
        x (int:str): This is not a valid type hint
        y (list[str, int]): This is also not valid
    """''',

    '''"""Extremely long single line docstring that goes on and on and doesn't break into multiple lines which might cause issues with certain parsers or display mechanisms especially if they have a character limit or assume a certain maximum line length for docstrings"""''',

    '''"""
    Class docstring
    """

    def method(self):
        """Method docstring"""
    ''',

    '',  # No docstring at all

    '''"""
    Docstring with markdown-like formatting

    # Header

    - Bullet point

    1. Numbered list

    `inline code`

    **bold text**
    """''',

    'r"""Raw string docstring with escape characters: \\n \\t \\r"""'
]

def test_docstring_parser():
    for i, docstring in enumerate(docstring_edge_cases):
        try:
            result = Parse(docstring)
            print(f"Case {i + 1} parsed successfully\nResult: ", result)

        except Exception as e:
            print(f"Error parsing case {i + 1}: {str(e)}")


# test_docstring_parser()
