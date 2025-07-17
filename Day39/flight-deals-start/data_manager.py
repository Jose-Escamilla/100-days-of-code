from dotenv import load_dotenv
import requests
import os
import base64

# Load environment variables from .env file
load_dotenv()

class DataManager:
    """
    This class is responsible for interacting with the Google Sheet via the Sheety API.
    It can retrieve destination data and update IATA codes and prices in the sheet.
    """

    def __init__(self):
        """
        Initializes the DataManager with Sheety API credentials and endpoint from environment variables.
        """
        self.sheety_endpoint = os.getenv("SHEETY_ENDPOINT")
        self.sheety_token = os.getenv("SHEETY_TOKEN")
        self.sheety_username = os.getenv("SHEETY_USERNAME")
        self.sheety_password = os.getenv("SHEETY_PASSWORD")
        
        # Debug: Print loaded credentials (be careful with this in production)
        print(f"🔧 Sheety Endpoint: {self.sheety_endpoint}")
        print(f"🔧 Has Token: {'Yes' if self.sheety_token else 'No'}")
        print(f"🔧 Has Username: {'Yes' if self.sheety_username else 'No'}")

    def get_destination_data(self):
        """
        Retrieves the destination data from the Google Sheet via a GET request to Sheety.
        
        Returns:
            list: A list of dictionaries representing each row in the Google Sheet.
        """
        # Try different authentication methods
        headers = {}
        
        if self.sheety_token:
            # If using Bearer token
            if self.sheety_token.startswith('Basic '):
                headers["Authorization"] = self.sheety_token
            else:
                headers["Authorization"] = f"Bearer {self.sheety_token}"
        
        try:
            if self.sheety_username and self.sheety_password:
                # Use Basic Auth with username/password
                response = requests.get(
                    url=self.sheety_endpoint, 
                    headers=headers,
                    auth=(self.sheety_username, self.sheety_password)
                )
            else:
                # Use only headers
                response = requests.get(url=self.sheety_endpoint, headers=headers)
            
            response.raise_for_status()
            print(f"✅ GET {response.status_code}: Data retrieved successfully.")
            data = response.json()
            
            # Debug: Print the structure of the response
            print(f"🔍 Response keys: {list(data.keys())}")
            print(f"🔍 Full response structure: {data}")
            
            # The object in Sheety is "prices"
            if "prices" in data:
                sheet_data = data["prices"]
                print(f"🔍 Found {len(sheet_data)} rows in prices")
                if sheet_data:
                    print(f"🔍 Sample row keys: {list(sheet_data[0].keys())}")
                return sheet_data
            else:
                print(f"❌ 'prices' key not found in response. Available keys: {list(data.keys())}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error retrieving data: {e}")
            return []

    def update_destination_codes(self, data):
        """
        Updates the IATA codes and lowest prices in the Google Sheet using a PUT request per row.

        Args:
            data (list): A list of destination dictionaries.
        """
        for destination in data:
            # Skip if no valid data to update
            if not destination.get("iataCode") or destination.get("lowestPrice") in ["N/A", None]:
                print(f"⏭️ Skipping row {destination.get('id', 'unknown')} - No valid flight data")
                continue
                
            row_id = destination["id"]
            endpoint = f"{self.sheety_endpoint}/{row_id}"

            # Sheety expects the data nested under the sheet name "prices"
            # Using the exact column names from your Google Sheet
            new_data = {
                "price": {  # This should match your sheet object name in Sheety
                    "iataCode": destination["iataCode"],
                    "lowestPrice": destination["lowestPrice"]
                }
            }
            
            print(f"🔄 Updating row {row_id}")
            print(f"🔄 Endpoint: {endpoint}")
            print(f"🔄 Data: {new_data}")
            
            try:
                # Prepare headers
                headers = {"Content-Type": "application/json"}
                
                if self.sheety_token:
                    if self.sheety_token.startswith('Basic '):
                        headers["Authorization"] = self.sheety_token
                    else:
                        headers["Authorization"] = f"Bearer {self.sheety_token}"
                
                # Make the PUT request
                if self.sheety_username and self.sheety_password:
                    response = requests.put(
                        url=endpoint,
                        json=new_data,
                        headers=headers,
                        auth=(self.sheety_username, self.sheety_password)
                    )
                else:
                    response = requests.put(
                        url=endpoint,
                        json=new_data,
                        headers=headers
                    )
                
                print(f"📡 Response Status: {response.status_code}")
                print(f"📡 Response Text: {response.text}")
                
                response.raise_for_status()
                print(f"✅ Updated row {row_id}: IATA={destination['iataCode']} | Price={destination['lowestPrice']}")
                
            except requests.exceptions.HTTPError as err:
                print(f"❌ HTTP Error updating row {row_id}: {err}")
                print(f"🔎 Status Code: {response.status_code}")
                print(f"🔎 Response: {response.text}")
                
                # Try with "prices" instead of "price"
                if response.status_code == 422 or response.status_code == 400:
                    print("🔄 Trying with 'prices' key...")
                    alternative_data = {
                        "prices": {
                            "iataCode": destination["iataCode"],
                            "lowestPrice": destination["lowestPrice"]
                        }
                    }
                    
                    try:
                        if self.sheety_username and self.sheety_password:
                            response = requests.put(
                                url=endpoint,
                                json=alternative_data,
                                headers=headers,
                                auth=(self.sheety_username, self.sheety_password)
                            )
                        else:
                            response = requests.put(
                                url=endpoint,
                                json=alternative_data,
                                headers=headers
                            )
                        
                        response.raise_for_status()
                        print(f"✅ Updated row {row_id} with 'prices' key")
                    except requests.exceptions.HTTPError:
                        print(f"❌ Both 'price' and 'prices' keys failed for row {row_id}")
                        print(f"🔎 Final Response: {response.text}")
                        
            except requests.exceptions.RequestException as e:
                print(f"❌ Request Error updating row {row_id}: {e}")