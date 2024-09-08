import inspect
import os
import sys
from examples.tool import tool
sys.path.append("../src")
sys.path.append("../")
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

class YouTubeDataAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    @tool
    def search_videos(self, query, max_results=5, order='relevance', video_duration='any', video_type='any'):
        """
        Searches for videos based on the given query and parameters.
        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.
            order (str): The order of the search results.
            video_duration (str): Duration of the videos to search for.
            video_type (str): Type of videos to search for.
        Returns:
            list: A list of dictionaries containing video information.
        """
        request = self.youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            order=order,
            type='video',
            videoDuration=video_duration,
            videoType=video_type
        )
        response = request.execute()

        videos = []
        for item in response.get('items', []):
            video_info = {
                'videoId': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channelTitle': item['snippet']['channelTitle'],
                'publishedAt': item['snippet']['publishedAt']
            }
            videos.append(video_info)

        return videos

    @tool
    def get_video_details(self, video_ids):
        """
        Gets the view count for the specified video IDs.
        Args:
            video_ids (list): A list of video IDs.
        Returns:
            dict: A dictionary mapping video IDs to their view counts.
        """
        request = self.youtube.videos().list(
            part='statistics',
            id=','.join(video_ids)
        )
        response = request.execute()

        video_details = {}
        for item in response.get('items', []):
            video_id = item['id']
            view_count = int(item['statistics'].get('viewCount', 0))
            video_details[video_id] = view_count

        return video_details

    def get_function_map(self):
        """
        Returns a dictionary mapping function names to their references.
        Returns:
            dict: A dictionary where keys are function names and values are function references.
        """
        return {
            'search_videos': self.search_videos,
            'get_video_details': self.get_video_details
        }

    def call_method(self, function_call):
        """
        Calls a method based on the provided function call structure.
        Args:
            function_call (dict): A dictionary containing the function name and parameters.
                                  Format: {
                                      "function": "function_name",
                                      "params": {
                                          "param1": "value1",
                                          "param2": "value2"
                                      }
                                  }
        Returns:
            The result of the called function.
        Raises:
            ValueError: If the function is not found or if there's an error in calling the function.
        """
        function_name = function_call.get("function")
        params = function_call.get("params", {})

        function_map = self.get_function_map()
        if function_name not in function_map:
            raise ValueError(f"Function '{function_name}' not found")

        try:
            return function_map[function_name](**params)
        except Exception as e:
            raise ValueError(f"Error calling function '{function_name}': {str(e)}")
