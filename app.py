from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests
import tweepy
from transformers import pipeline

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Task 1: Gather data
def get_hot_topics(city, api_key):
    news_source = "bbc-news"
    endpoint = "https://newsapi.org/v2/top-headlines"
    params = {"apiKey": api_key, "country": "in", "q": city}

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        top_headlines = [article["title"] for article in data.get("articles", [])[:5]]
        return top_headlines
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Task 2: Gather relevant discussions
def get_twitter_discussions(api_key, api_secret_key, access_token, access_token_secret, topic):
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    try:
        tweets = tweepy.Cursor(api.search, q=topic, tweet_mode='extended').items(10)

        discussions = []
        for tweet in tweets:
            user_name = tweet.user.screen_name
            tweet_text = tweet.full_text
            created_at = tweet.created_at.strftime("%Y-%m-%d %H:%M:%S")

            discussions.append({
                "user": user_name,
                "text": tweet_text,
                "created_at": created_at
            })

        return discussions
    except tweepy.TweepError as e:
        print(f"Error: {e}")
        return None

# Task 3: Analyze gathered information
def analyze_discussions(discussions):
    sentiment_analyzer = pipeline("sentiment-analysis")

    summaries = [discussion['text'] for discussion in discussions]
    sentiments = sentiment_analyzer(summaries)

    return {
        "highlights": summaries,
        "sentiments": sentiments
    }

# FastAPI routes
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/results", response_class=HTMLResponse)
def read_item(request: Request, city: str = Form(...), topic: str = Form(...)):
    twitter_api_key = "your_twitter_api_key"  # Replace with your actual Twitter API key
    twitter_api_secret_key = "your_twitter_api_secret_key"  # Replace with your actual Twitter API secret key
    twitter_access_token = "your_twitter_access_token"  # Replace with your actual Twitter access token
    twitter_access_token_secret = "your_twitter_access_token_secret"  # Replace with your actual Twitter access token secret

    # Task 1: Gather data
    hot_topics = get_hot_topics(city, "your_news_api_key")  # Replace with your actual News API key

    # Task 2: Gather relevant discussions
    twitter_discussions = get_twitter_discussions(
        twitter_api_key,
        twitter_api_secret_key,
        twitter_access_token,
        twitter_access_token_secret,
        topic
    )

    if twitter_discussions:
        # Task 3: Analyze gathered information
        discussions_info = analyze_discussions(twitter_discussions)
        return templates.TemplateResponse("results.html", {"request": request, "city": city, "hot_topics": hot_topics, "discussions_info": discussions_info})
    else:
        return "Failed to fetch Twitter discussions. Please check your Twitter API keys and network connection."
