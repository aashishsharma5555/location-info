import requests
from django.shortcuts import render
from django.conf import settings

# WeatherAPI Key (Replace with your actual API key)
WEATHER_API_KEY = '2aea3085bbe74c0fa9274127252301'

# NewsAPI Key (Replace with your actual API key)
NEWS_API_KEY = '7a5e167fc4674fbd89b8127b04af71ff'

# Function to fetch weather data for a given location
def fetch_weather(location):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise HTTPError for bad responses
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {"error": "HTTP error occurred while fetching weather data."}
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return {"error": "An error occurred while fetching weather data."}

# Function to fetch a brief description about the location from Wikipedia
def fetch_location_description(location):
    wikipedia_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{location}"
    try:
        response = requests.get(wikipedia_url)
        response.raise_for_status()  # Will raise HTTPError for bad responses
        data = response.json()
        
        description = data.get("extract", "Description not available.")
        
        description_words = description.split()
        truncated_description = " ".join(description_words[:250])  # Get first 250 words
        return truncated_description
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return "Error occurred while fetching description."
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return "An error occurred while fetching description."

# Function to fetch the latest news for the location
def fetch_latest_news(location):
    news_url = f"https://newsapi.org/v2/everything?q={location}&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(news_url)
        response.raise_for_status()  # Will raise HTTPError for bad responses
        data = response.json()
        articles = data.get("articles", [])
        
        # Extract titles and links from the news articles
        news = [{"title": article["title"], "url": article["url"]} for article in articles[:5]]  # Fetch top 5 articles
        return news
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return []
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return []

# Function to determine clothing suggestion based on temperature
def get_clothing_suggestion(temperature):
    suggestion = None
    links = {}

    if temperature <= 15:
        suggestion = "Wear a jacket."
        links = {
            'flipkart': 'https://www.flipkart.com/search?q=jackets',
            'myntra': 'https://www.myntra.com/search?q=jackets',
            'amazon': 'https://www.amazon.in/s?k=jacket+jackets'
        }
    elif 16 <= temperature <= 25:
        suggestion = "Wear a Full-Sleeve t-shirt and light jeans or trousers."
        links = {
            'flipkart': 'https://www.flipkart.com/search?q=full+sleeve+t-shirt+light+jeans',
            'myntra': 'https://www.myntra.com/search?q=full+sleeve+t-shirt+light+jeans',
            'amazon': 'https://www.amazon.in/s?k=full+sleeve+t-shirt+light+jeans'
        }
    else:
        suggestion = "Wear a half t-shirt and shorts. Don't forget your sunglasses!"
        links = {
            'flipkart': 'https://www.flipkart.com/search?q=half+t-shirt+shorts',
            'myntra': 'https://www.myntra.com/search?q=half+t-shirt+shorts',
            'amazon': 'https://www.amazon.in/s?k=half+t-shirt+shorts'
        }

    return suggestion, links

# View function for home page and fetching weather, clothing suggestions, location description, and news
def home(request):
    suggestion = None
    links = {}
    location = None
    destination_weather = None
    destination_suggestion = None
    location_description = None
    latest_news = []

    if request.method == "GET" and 'location' in request.GET:
        location = request.GET['location']

        # Fetch weather data for the location using WeatherAPI
        weather_data = fetch_weather(location)

        if 'error' in weather_data:
            suggestion = weather_data["error"]
        else:
            # Get the temperature at the destination
            temperature = weather_data['current']['temp_c']
            destination_weather = weather_data['current']

            # Try to extract latitude/longitude from WeatherAPI response (if present)
            loc_info = weather_data.get('location', {}) if isinstance(weather_data, dict) else {}
            map_lat = loc_info.get('lat')
            map_lon = loc_info.get('lon')

            # Get clothing suggestion and links
            destination_suggestion, links = get_clothing_suggestion(temperature)

            # Fetch a brief description of the location from Wikipedia
            location_description = fetch_location_description(location)

            # Fetch latest news about the location
            latest_news = fetch_latest_news(location)

    return render(request, 'home.html', {
        'suggestion': suggestion,
        'location': location,
        'destination_weather': destination_weather,
        'destination_suggestion': destination_suggestion,
        'links': links,
        'location_description': location_description,
        'latest_news': latest_news,  # Pass the latest news to the template
        'map_lat': map_lat if 'map_lat' in locals() else None,
        'map_lon': map_lon if 'map_lon' in locals() else None,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    })
