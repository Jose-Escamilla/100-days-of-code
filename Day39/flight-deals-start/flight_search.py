from datetime import datetime, timedelta
from flight_data import FlightData
import requests
import os

class FlightSearch:
    """
    This class is responsible for interacting with the Amadeus Flight Search API.
    It handles authentication, retrieving IATA codes for cities, and searching for flights.
    """

    def __init__(self):
        """
        Initializes the FlightSearch object by loading the API credentials and obtaining an access token.
        """
        self.api_key = os.getenv("AMADEUS_API_KEY")
        self.api_secret = os.getenv("AMADEUS_API_SECRET")        
        self.token = self.get_access_token()

    def get_access_token(self):
        """
        Authenticates with the Amadeus API and retrieves an access token.

        Returns:
            str: The access token.
        """
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }    
        body = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()
        token = response.json()["access_token"]
        return token

    def get_iata_code(self, city_name):
        """
        Gets the IATA airport code for a given city using the Amadeus API.

        Args:
            city_name (str): The name of the city to look up.

        Returns:
            str: The IATA code if found, otherwise an empty string.
        """
        print(f"🔍 Looking up IATA code for: {city_name}")  # Debug print
        url = "https://test.api.amadeus.com/v1/reference-data/locations"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "keyword": city_name,
            "subType": "CITY",
            "page[limit]": 1
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            print(f"✅ IATA code for {city_name}: {data['data'][0]['iataCode']}")  # Debug print
            return data["data"][0]["iataCode"]
        except (IndexError, KeyError):
            print(f"❌ IATA code not found for: {city_name}")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching IATA code for '{city_name}': {e}")
            return ""

    def search_flights(self, origin_city_code, destination_city_code):
        """
        Searches for the cheapest round-trip flight between two city codes using the Amadeus API.

        Args:
            origin_city_code (str): The IATA code of the origin city.
            destination_city_code (str): The IATA code of the destination city.

        Returns:
            FlightData: An object containing flight information (or "N/A" values if not found).
        """
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        tomorrow = datetime.now() + timedelta(days=1)
        six_months_later = datetime.now() + timedelta(days=180)

        params = {
            "originLocationCode": origin_city_code,
            "destinationLocationCode": destination_city_code,
            "departureDate": tomorrow.strftime("%Y-%m-%d"),
            "returnDate": six_months_later.strftime("%Y-%m-%d"),
            "adults": 1,
            # You may enable the next line to search only for non-stop flights
            # "nonStop": True,
            "currencyCode": "MXN",  # Change to "GBP" or other if needed
            "max": 1  # Return only the cheapest option
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()["data"][0]
            itinerary = data["itineraries"][0]
            segments = itinerary["segments"][0]
            return FlightData(
                price=data["price"]["total"],
                origin_airport=segments["departure"]["iataCode"],
                destination_airport=segments["arrival"]["iataCode"],
                out_date=segments["departure"]["at"].split("T")[0],
                return_date=itinerary["segments"][-1]["arrival"]["at"].split("T")[0]
            )
        except (IndexError, KeyError):
            print(f"⚠️ No flights found: {origin_city_code} → {destination_city_code}")
            return FlightData("N/A", "N/A", "N/A", "N/A", "N/A")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching flights {origin_city_code} → {destination_city_code}: {e}")
            return FlightData("N/A", "N/A", "N/A", "N/A", "N/A")
