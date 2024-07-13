from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tweepy
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Twitter API credentials
API_KEY = os.getenv('A56VF8V8Kre9Pz4of4Qoh6Wf8')
API_SECRET = os.getenv('tRt5n2TOB2RQhf492TECBnO2rRAv7gVGiWVMejydYXBgiNLxKy')
ACCESS_TOKEN = os.getenv('1793290897893085184-4co25BNFToHEbOZZeAMTSCTIJI7BvJ')
ACCESS_TOKEN_SECRET = os.getenv('rvNNGQ1PYBjp1qx3AZv93YYxUAZrrwTnlEBtGBwVKtLLU')

# FastAPI instance
app = FastAPI()

# Tweepy authentication
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Request model
class TweetThreadRequest(BaseModel):
    text: str

def split_text_into_tweets(text, max_length=280):
    """Splits the text into chunks that fit within the tweet character limit."""
    words = text.split()
    tweets = []
    current_tweet = ""

    for word in words:
        if len(current_tweet) + len(word) + 1 <= max_length:
            current_tweet += " " + word
        else:
            tweets.append(current_tweet.strip())
            current_tweet = word

    tweets.append(current_tweet.strip())  # Add the last tweet
    return tweets

@app.post("/create_thread/")
def create_twitter_thread(request: TweetThreadRequest):
    tweets = split_text_into_tweets(request.text)
    if not tweets:
        raise HTTPException(status_code=400, detail="No valid content provided")

    try:
        # Post the first tweet
        first_tweet = api.update_status(status=tweets[0])
        tweet_id = first_tweet.id

        # Post the subsequent tweets as replies
        for tweet in tweets[1:]:
            tweet_id = api.update_status(status=tweet, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True).id
       
        return {"status": "success", "message": "Twitter thread created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

