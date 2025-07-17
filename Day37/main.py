from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
import os

# ------🔐 1. Load environment variables ------
load_dotenv()
TOKEN = os.getenv("PIXELA_TOKEN")
USERNAME = os.getenv("PIXELA_USERNAME")


#pixela_endpoint = "https://pixe.la/v1/users"

# ------🌐 2. Define Pixela endpoints ------
pixela_endpoint = "https://pixe.la/v1/users"
graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"
pixel_endpoint = f"{graph_endpoint}/graph13"  # Graph ID

headers = {
    "X-USER-TOKEN": TOKEN
}

# ------👤 3. Create a user account (run once) ------
user_params = {
    "token": TOKEN,
    "username": USERNAME,
    "agreeTermsOfService": "yes",
    "notMinor": "yes",
}

# Uncomment to create the user (run only once)
# response = requests.post(url=pixela_endpoint, json=user_params)
# print(response.status_code)
# print(response.text)


# ------📊 4. Create a graph (run once) ------
#graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"

graph_config = {
    "id": "graph13",
    "name": "Reading Graph",
    "unit": "Pages",
    "type": "float",
    "color": "kuro",
}

# Uncomment to create the graph (run only once)
# response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)
# print(response.status_code)
# print(response.text)

# You can view the graph at:
# https://pixe.la/v1/users/YOUR_USERNAME/graphs/YOUR_GRAPH_ID.html

# ------🟩 5. Add today's pixel to the graph ------
#pixel_endpoint = f"{graph_endpoint}/graph13"
today = datetime.now().strftime("%Y%m%d")

pixel_config = {
    "date": today,
    "quantity": "3.5",
}

# Uncomment to add today's pixel
# response = requests.post(url=pixel_endpoint, json=pixel_config, headers=headers)
# print(response.status_code)
# print(response.text)

# ------✏️ 6. Update yesterday's pixel with PUT ------
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
update_endpoint = f"{pixel_endpoint}/{yesterday}"

pixel_update = {
    "quantity": "2.0"
}

# Uncomment to update yesterday's pixel
response = requests.put(url=update_endpoint, json=pixel_update, headers=headers)
print(response.status_code)
print(response.text)

# ------❌ 7. Delete yesterday's pixel with DELETE ------
delete_endpoint = f"{pixel_endpoint}/{yesterday}"

# Uncomment to delete yesterday's pixel
# response = requests.delete(url=delete_endpoint, headers=headers)
# print(response.status_code)
# print(response.text)
# https://pixe.la/v1/users/jose13esc/graphs/graph13.html