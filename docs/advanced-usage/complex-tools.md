---
layout: default
title: Creating Complex Tools
---

# Creating Complex Tools

While simple function-based tools are sufficient for many use cases, TinyTune also supports creating more complex tools with multiple methods and state.

## Class-Based Complex Tool

```python
from tinytune.tool import tool

class AdvancedWeatherTool:
    def __init__(self):
        self.api_key = "your_weather_api_key"

    @tool
    def get_current_weather(self, location: str):
        """
        Get current weather for a location.
        Args:
            location (str): The location to get weather for.
        Returns:
            dict: A dictionary containing current weather information.
        """
        # Implementation using self.api_key
        return {"temperature": 25, "condition": "Sunny"}

    @tool
    def get_forecast(self, location: str, days: int):
        """
        Get weather forecast for a location.
        Args:
            location (str): The location to get forecast for.
            days (int): Number of days for the forecast.
        Returns:
            list: A list of dictionaries containing forecast information.
        """
        # Implementation using self.api_key
        return [{"day": i, "temperature": 20 + i, "condition": "Partly Cloudy"} for i in range(days)]

    def get_function_map(self):
        return {name: func for name, func in vars(self.__class__).items() if isinstance(func, tuple)}

    def call_method(self, function_call):
        function_name = function_call.get("function")
        params = function_call.get("params", {})
        params["self"] = self

        function_map = self.get_function_map()
        if function_name not in function_map:
            raise ValueError(f"Function '{function_name}' not found")

        return function_map[function_name][0](**params)

weather_tool = AdvancedWeatherTool()
```

## Using Complex Tools in Prompt Jobs

```python
@prompt_job(id="weather_report", context=your_context)
def WeatherReportJob(id: str, context: LLMContext, prevResult: Any):
    current_weather = weather_tool.get_current_weather("New York")
    forecast = weather_tool.get_forecast("New York", 5)

    report = f"Current weather in New York: {current_weather['temperature']}°C, {current_weather['condition']}\n\n"
    report += "5-day forecast:\n"
    for day in forecast:
        report += f"Day {day['day']}: {day['temperature']}°C, {day['condition']}\n"

    return (context.Prompt(Message("user", f"Summarize this weather report:\n\n{report}"))
            .Run(stream=True)
            .Messages[-1])
```

## Best Practices for Complex Tools

1. Use clear and descriptive method names.
2. Provide comprehensive docstrings for each method.
3. Implement proper error handling within the tool methods.
4. Use type hints for better integration with TinyTune's type checking.
5. Consider implementing a caching mechanism for expensive operations.

## Example: Database Tool

```python
import sqlite3
from tinytune.tool import tool

class DatabaseTool:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    @tool
    def execute_query(self, query: str):
        """
        Execute an SQL query.
        Args:
            query (str): The SQL query to execute.
        Returns:
            list: A list of tuples containing the query results.
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            return f"Error executing query: {str(e)}"

    @tool
    def insert_data(self, table: str, data: dict):
        """
        Insert data into a table.
        Args:
            table (str): The name of the table.
            data (dict): A dictionary of column names and values.
        Returns:
            str: A message indicating success or failure.
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, list(data.values()))
            self.conn.commit()
            return "Data inserted successfully"
        except sqlite3.Error as e:
            return f"Error inserting data: {str(e)}"

    def __del__(self):
        self.conn.close()

db_tool = DatabaseTool("your_database.db")
```

This example shows how to create a complex tool for interacting with a SQLite database, demonstrating state management (database connection) and multiple methods for different operations.
