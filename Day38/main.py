from dotenv import load_dotenv
from datetime import datetime
import requests
import os

# ------🔐 1. Load environment variables ------
load_dotenv()
APP_ID = os.getenv("APP_ID")
API_KEY = os.getenv("API_KEY")
SHEETY_TOKEN = os.getenv("SHEETY_TOKEN")
ENDPOINT = "https://trackapi.nutritionix.com/v2/natural/exercise"
POST_ENDPOINT = os.getenv("POST_ENDPOINT") # obtained from POST on Sheety 

# ------📡 Nutritionix API ------

headers = {
    "x-app-id": APP_ID,
    "x-app-key": API_KEY,
    "Content-Type": "application/json",
}


parameters = {
    "query": "I ran 3 kilometers and did 20 minutes of swimming.",
    "gender": "male",
    "weight_kg": 60.2,
    "height_cm": 163,
    "age": 30,
}

response = requests.post(url=ENDPOINT, headers=headers, json=parameters)
#print(response.json())
exercises = response.json()["exercises"]

# ------📤 Enviar a Google Sheet ------
sheety_headers = {
    "Authorization": f"Basic {SHEETY_TOKEN}"
}

for exercise in exercises:
    workout_data = {
        "workout": {
            "date": datetime.now().strftime("%d/%m/%Y"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "exercise": exercise["name"].title(),
            "duration": round(exercise["duration_min"]),
            "calories": round(exercise["nf_calories"]),
        }
    }
    post_response = requests.post(url=POST_ENDPOINT, json=workout_data, headers=sheety_headers)
    print(post_response.status_code, post_response.text)
    print(f"Sent to Google Sheet: {workout_data['workout']}")
