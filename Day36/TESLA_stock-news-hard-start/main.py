from dotenv import load_dotenv
from twilio.rest import Client
import os
import requests

# Set the stock symbol and company name
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# Define API endpoints
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# Load environment variables from .env file
load_dotenv()
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


## STEP 1: Use https://newsapi.org/docs/endpoints/everything
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
#HINT 1: Get the closing price for yesterday and the day before yesterday. Find the positive difference between the two prices. e.g. 40 - 20 = -20, but the positive difference is 20.
#HINT 2: Work out the value of 5% of yerstday's closing stock price. 
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": ALPHAVANTAGE_API_KEY
}

alph_response = requests.get(STOCK_ENDPOINT, params=stock_params)
data = alph_response.json()

# Check for expected data
if "Time Series (Daily)" not in data:
    print("❌ Error en la respuesta de la API:")
    print(data)  # This will show if it is an error due to a limit, invalid key, etc.
    exit()

# Convert the time series into a list of daily prices
data_list = [value for (key, value) in data["Time Series (Daily)"].items()]
yesterday_data = data_list[0]
day_before_yesterday_data = data_list[1]

# Extract the closing prices
yesterday_closing_price = float(yesterday_data["4. close"])
day_before_yesterday_closing_price = float(day_before_yesterday_data["4. close"])

# Calculate the price difference and percentage change
difference = yesterday_closing_price - day_before_yesterday_closing_price
up_down = "🔺" if difference > 0 else "🔻"
diff_percent = round((difference / day_before_yesterday_closing_price) * 100, 2)

# print(f"Yesterday: {yesterday_closing_price}")
# print(f"Day Before Yesterday: {day_before_yesterday_closing_price}")
# print(f"Change: {up_down}{diff_percent}%")

## STEP 2: Use https://newsapi.org/docs/endpoints/everything
# Instead of printing ("Get News"), actually fetch the first 3 articles for the COMPANY_NAME. 
#HINT 1: Think about using the Python Slice Operator
if abs(diff_percent) > 5:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }
    new_response = requests.get(NEWS_ENDPOINT, params=news_params)
    news_data = new_response.json()
    
    # Defensive check in case no articles are found
    if "articles" not in news_data or not news_data["articles"]:
        print("⚠️ No news articles found.")
        exit()

    articles = news_data["articles"][:3]  # Get the top 3 articles
    # print(articles)

    ## STEP 3: Use twilio.com/docs/sms/quickstart/python
    # Send a separate message with each article's title and description to your phone number. 
    #HINT 1: Consider using a List Comprehension.
    
    formatted_articles = [
        f"{STOCK}: {up_down}{diff_percent}%\nHeadline: {article['title']}\nBrief: {article['description']}"
        for article in articles
    ]

    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    for message_body in formatted_articles:
        message = client.messages.create(
            body=message_body,
            from_=os.getenv("TWILIO_PHONE"),  # Twilio phone number
            to=os.getenv("MY_PHONE")        # Your personal phone number
        )
        print(f"✅ SMS sent. SID: {message.sid}")
        print(message)

#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

