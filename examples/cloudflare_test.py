import requests
import os
import sys
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoint
cloudflare_url = f"https://api.cloudflare.com/client/v4/accounts/{os.getenv('CLOUDFLARE_ID')}/ai/run/@cf/meta/llama-3.2-11b-vision-instruct"

# Authorization headers
headers = {
    "Authorization": f"Bearer {os.getenv('CLOUDFLARE_KEY')}",
    "Content-Type": "application/json",
}

# Read the image file in binary mode
image_path = sys.argv[1]

with open(image_path, "rb") as image_file:
    image_data = image_file.read()

# Encode the image as base64
encoded_image = base64.b64encode(image_data).decode("utf-8")

# Construct the request payload with image data
data = {
    "prompt": "What is in this image?",
    "image": f"data:image/jpeg;base64,{encoded_image}",
}

# Send the POST request
response = requests.post(cloudflare_url, headers=headers, json=data)

# Check and print the response
if response.status_code == 200:
    print(response.json())  # Output the response
else:
    print(f"Request failed: {response.status_code}, {response.text}")
