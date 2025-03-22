import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import tweepy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
MOCK_TWITTER = os.getenv("MOCK_TWITTER", "False").lower() == "true"

# Initialize FastAPI app
app = FastAPI()

# Twitter API setup (only if not mocking)
if not MOCK_TWITTER:
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    twitter_api = tweepy.API(auth)

# Request body model for the API endpoint
class Caption(BaseModel):
    text: str

def summarize_caption(caption: str) -> str:
    """
    Summarize an Instagram caption using OpenAI's ChatGPT into 280 characters or less.
    
    Args:
        caption (str): The original Instagram caption.
    
    Returns:
        str: A summary within 280 characters.
    
    Raises:
        Exception: If the OpenAI API call fails.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize the following Instagram caption in 280 characters or less: {caption}"}
            ],
            max_tokens=70  # Approximately 280 characters
        )
        summary = response.choices[0].message['content'].strip()
        # Ensure summary fits within 280 characters
        if len(summary) > 280:
            summary = summary[:280].rsplit(' ', 1)[0]
        return summary
    except openai.error.OpenAIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")

@app.post("/post-tweet", summary="Post a summarized Instagram caption to Twitter")
async def post_tweet(caption: Caption):
   """
    Summarize an Instagram caption using an LLM and post it to Twitter.

    ### Usage
    Send a POST request with the original Instagram caption in the request body.

    ### Input
    - `text`: The original Instagram caption (string, required)

    ### Output
    - Success: `{"message": "Tweet posted successfully"}`
    - Error: `{"error": "Error message"}`

    ### Example
    **Request:**
    ```json
    {
        "text": "Enjoying a beautiful sunset at the beach with friends, the perfect end to a great day!"
    }"
    """