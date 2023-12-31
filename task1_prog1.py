import requests

def get_hot_topics(city, api_key):
    news_source = "bbc-news"
    endpoint = "https://newsapi.org/v2/top-headlines"
    params = {"apiKey": api_key, "country": "in", "q": city}

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()
        top_headlines = [article["title"] for article in data.get("articles", [])[:5]]
        return top_headlines
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# test case 1
api_key = "641254251e2244c79c2de4c09d9130df"
city_name = "New Delhi"
hot_topics = get_hot_topics(city_name, api_key)

if hot_topics:
    print(f"Top 5 topics in {city_name} according to BBC News:")
    for idx, topic in enumerate(hot_topics, 1):
        print(f"{idx}. {topic}")
else:
    print("Failed to fetch hot topics. Please check your API key and network connection.")
