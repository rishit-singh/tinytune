import os
import sys
from tinytune.tool import tool

sys.path.append("../src")
sys.path.append("../")

from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

class YouTubeDataAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    @tool
    def search_videos(
        self,
        query,
        max_results=5,
        order="relevance",
        video_duration="any",
        video_type="any",
    ):
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
            part="snippet",
            maxResults=max_results,
            order=order,
            type="video",
            videoDuration=video_duration,
            videoType=video_type,
        )
        response = request.execute()

        videos = []
        for item in response.get("items", []):
            video_info = {
                "videoId": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "channelTitle": item["snippet"]["channelTitle"],
                "publishedAt": item["snippet"]["publishedAt"],
            }
            videos.append(video_info)

        return videos

    @tool
    def get_video_details(self, video_ids):
        """
        Gets detailed information for the specified video IDs.
        Args:
            video_ids (list): A list of video IDs.
        Returns:
            dict: A dictionary mapping video IDs to their details.
        """
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics", id=",".join(video_ids)
        )
        response = request.execute()

        video_details = {}
        for item in response.get("items", []):
            video_id = item["id"]
            video_details[video_id] = {
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "viewCount": int(item["statistics"].get("viewCount", 0)),
                "likeCount": int(item["statistics"].get("likeCount", 0)),
                "commentCount": int(item["statistics"].get("commentCount", 0)),
                "duration": item["contentDetails"]["duration"],
            }

        return video_details

    @tool
    def get_channel_info(self, channel_id):
        """
        Gets information about a YouTube channel.
        Args:
            channel_id (str): The ID of the YouTube channel.
        Returns:
            dict: A dictionary containing channel information.
        """
        request = self.youtube.channels().list(part="snippet,statistics", id=channel_id)
        response = request.execute()

        if "items" in response:
            channel = response["items"][0]
            return {
                "title": channel["snippet"]["title"],
                "description": channel["snippet"]["description"],
                "subscriberCount": int(channel["statistics"]["subscriberCount"]),
                "viewCount": int(channel["statistics"]["viewCount"]),
                "videoCount": int(channel["statistics"]["videoCount"]),
            }
        return None

    @tool
    def get_playlist_items(self, playlist_id, max_results=50):
        """
        Gets items from a specified playlist.
        Args:
            playlist_id (str): The ID of the playlist.
            max_results (int): Maximum number of results to return.
        Returns:
            list: A list of dictionaries containing playlist item information.
        """
        request = self.youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id, maxResults=max_results
        )
        response = request.execute()

        playlist_items = []
        for item in response.get("items", []):
            playlist_items.append(
                {
                    "videoId": item["snippet"]["resourceId"]["videoId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "publishedAt": item["snippet"]["publishedAt"],
                }
            )
        return playlist_items

    @tool
    def get_comments(self, video_id, max_results=100):
        """
        Gets comments for a specified video.
        Args:
            video_id (str): The ID of the video.
            max_results (int): Maximum number of comments to return.
        Returns:
            list: A list of dictionaries containing comment information.
        """
        request = self.youtube.commentThreads().list(
            part="snippet", videoId=video_id, maxResults=max_results
        )
        response = request.execute()

        comments = []
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(
                {
                    "author": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "likeCount": comment["likeCount"],
                    "publishedAt": comment["publishedAt"],
                }
            )
        return comments

    @tool
    def search_channels(self, query, max_results=5):
        """
        Searches for YouTube channels based on a query.
        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.
        Returns:
            list: A list of dictionaries containing channel information.
        """
        request = self.youtube.search().list(
            q=query, part="snippet", maxResults=max_results, type="channel"
        )
        response = request.execute()

        channels = []
        for item in response.get("items", []):
            channels.append(
                {
                    "channelId": item["id"]["channelId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "thumbnailUrl": item["snippet"]["thumbnails"]["default"]["url"],
                }
            )
        return channels

    @tool
    def get_video_categories(self, region_code="US"):
        """
        Gets a list of video category IDs for a specified country.
        Args:
            region_code (str): The region code for the country.
        Returns:
            list: A list of dictionaries containing category information.
        """
        request = self.youtube.videoCategories().list(
            part="snippet", regionCode=region_code
        )
        response = request.execute()

        categories = []
        for item in response.get("items", []):
            categories.append({"id": item["id"], "title": item["snippet"]["title"]})
        return categories

    def get_function_map(self):
        """
        Returns a dictionary mapping function names to their references.
        Returns:
            dict: A dictionary where keys are function names and values are function references.
        """
        return {
            name: func
            for name, func in vars(self.__class__).items()
            if isinstance(func, tuple)
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
        params["self"] = self

        if "q" in params.keys():
            params["query"] = params["q"]
            params.pop("q")

        function_map = self.get_function_map()

        if function_name not in function_map:
            raise ValueError(f"Function '{function_name}' not found")

        try:
            print("function: ", function_name, " ", params)
            print(function_map[function_name])
            return function_map[function_name][0](**params)

        except Exception as e:
            raise ValueError(f"Error calling function '{function_name}': {str(e)}")
