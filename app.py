from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests
import tweepy
import openai

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Replace these placeholder values with your actual API keys
twitter_api_key = "GSwgij3e1HRNYJyT14FzDqVvI"
twitter_api_secret_key = "dfdqG2jt7Hdkgkv2q6H18D0JDn0ITFQqj8l9zk58Gxoxj4FWr7"
twitter_access_token = "1722324471053254656-zNKWBlRJYrlhBfmKK4ZQwF0N2nLUN0"
twitter_access_token_secret = "UFAA8piH7mzGZPQqWKwKoZAhqiIPN54t5nBhxOcSbPIOO"
news_api_key = "641254251e2244c79c2de4c09d9130df"
openai.api_key = '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'

# Task 1: Gather data - Hot Topics from News API
def get_hot_topics(city, api_key):
    endpoint = "https://newsapi.org/v2/top-headlines?country=in&apiKey=641254251e2244c79c2de4c09d9130df"
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

# Task 2: Gather relevant discussions - Twitter
def get_twitter_discussions(api_key, api_secret_key, access_token, access_token_secret, topic):
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    try:
        tweets = tweepy.Cursor(api.search_tweets, q=topic, tweet_mode='extended').items(10)

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
    except Exception as e:
        print(f"Error: {e}")
        return None

# Task 3: Analyze gathered information - OpenAI GPT-3
def analyze_discussions(discussions):
    summaries = [discussion['text'] for discussion in discussions]

    # Use GPT-3 to generate a summary
    gpt3_summary = generate_gpt3_summary(summaries)

    return {
        "highlights": summaries,
        "gpt3_summary": gpt3_summary
    }

def generate_gpt3_summary(input_texts):
    prompt = "\n".join(input_texts)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# FastAPI routes
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/results", response_class=HTMLResponse)
def read_item(request: Request, city: str = Form(...)):
    # Task 1: Gathering data - Hot Topics
    hot_topics = get_hot_topics(city, news_api_key)

    if hot_topics:
        # Task 2: Gathering relevant discussions - Twitter, and Task 3: Analyzing gathered information
        discussions_info = []
        for topic in hot_topics:
            twitter_discussions = get_twitter_discussions(
                twitter_api_key,
                twitter_api_secret_key,
                twitter_access_token,
                twitter_access_token_secret,
                topic
            )
            if twitter_discussions:
                # Task 3: Analyzing gathered information
                discussions_info.extend(analyze_discussions(twitter_discussions))

        return templates.TemplateResponse("results.html", {"request": request, "city": city, "hot_topics": hot_topics, "discussions_info": discussions_info})
    else:
        return "Failed to fetch hot topics. Please check your API keys and network connection."

