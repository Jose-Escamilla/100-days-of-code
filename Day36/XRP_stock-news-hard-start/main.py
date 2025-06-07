# Import required libraries
from dotenv import load_dotenv
from twilio.rest import Client
import os
import requests

# Load environment variables from .env file
load_dotenv()

# Define constants for the cryptocurrency and related company
STOCK = "XRP"
COMPANY_NAME = "Ripple Labs"

# Define API endpoints
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
MARKET = "USD"

# Load API keys from environment variables
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# STEP 1: Fetch daily crypto price data from Alpha Vantage
parameters = {
    "function": "DIGITAL_CURRENCY_DAILY",
    "symbol": STOCK,
    "market": MARKET,
    "apikey": ALPHAVANTAGE_API_KEY
}

try:
    response = requests.get(STOCK_ENDPOINT, params=parameters)
    response.raise_for_status()  # Raise an error if the request failed
    response_data = response.json()

    print(f"API Key loaded: {'Yes' if ALPHAVANTAGE_API_KEY else 'No'}")
    print("Response keys:", response_data.keys())

    # Check for API errors or rate limits
    if "Error Message" in response_data:
        print(f"API error: {response_data['Error Message']}")
        exit()

    if "Note" in response_data:
        print(f"API rate limit message: {response_data['Note']}")
        exit()

    # Extract the price data
    data = response_data["Time Series (Digital Currency Daily)"]

except requests.exceptions.RequestException as e:
    print(f"Error fetching data from Alpha Vantage: {e}")
    exit()
except KeyError as e:
    print(f"Missing expected data key: {e}")
    print("Full response:", response_data)
    exit()
else:
    # Get the two most recent trading dates
    dates = list(data.keys())
    yesterday = dates[0]
    day_before = dates[1]

    # Get the closing prices for both days
    close_yesterday = float(data[yesterday]["4. close"])
    close_day_before = float(data[day_before]["4. close"])

    # Calculate absolute difference and percent change
    difference = abs(close_yesterday - close_day_before)
    percentage_change = (difference / close_day_before) * 100

# Print price summary
print(f"Yesterday's Price: ${close_yesterday:.4f}")
print(f"Day Before's Price: ${close_day_before:.4f}")
print(f"Percentage Change: {percentage_change:.2f}%")

# STEP 2: Fetch news articles if price change is significant
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Define threshold for "significant" price movement
if percentage_change > 0.3:
    print("Significant change detected — fetching news...")

    news_params = {
        "q": COMPANY_NAME,
        "apiKey": NEWS_API_KEY,  # Correct spelling is "apiKey"
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 3,
    }

    try:
        news_response = requests.get(NEWS_ENDPOINT, params=news_params)
        news_response.raise_for_status()
        news_data = news_response.json()

        if "articles" not in news_data:
            print("No articles found in the response.")
            print("News API response:", news_data)
            exit()

        articles = news_data["articles"]

        # Determine price trend direction
        up_down = "🔺" if close_yesterday > close_day_before else "🔻"
        percent_str = f"{percentage_change:.2f}%"

        # STEP 3: Send a separate SMS for each article
        for article in articles:
            headline = article.get("title", "No title available")
            brief = article.get("description", "No description available")

            # Truncate long descriptions for SMS readability
            if brief and len(brief) > 200:
                brief = brief[:200] + "..."

            message = (
                f"{STOCK}: {up_down}{percent_str}\n"
                f"Headline: {headline}\n"
                f"Brief: {brief}"
            )

            print("Message to be sent:")
            print(message)
            print("-" * 50)

            # Send the SMS via Twilio
            try:
                sms = client.messages.create(
                    body=message,
                    from_=os.getenv("TWILIO_PHONE"),  # Twilio phone number
                    to=os.getenv("MY_PHONE")        # Your personal phone number
                )
                print(f"SMS sent successfully. SID: {sms.sid}")
            except Exception as e:
                print(f"Error sending SMS: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
    except KeyError as e:
        print(f"Error processing news data: {e}")

else:
    print("No significant price change — no news will be sent.")
