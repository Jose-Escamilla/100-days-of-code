from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager
from pprint import pprint
import os

# Verify environment variables are loaded
print("🔧 Checking environment variables...")
required_vars = ["SHEETY_ENDPOINT", "AMADEUS_API_KEY", "AMADEUS_API_SECRET"]
twilio_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER", "RECIPIENT_PHONE_NUMBER"]

for var in required_vars:
    if os.getenv(var):
        print(f"✅ {var}: Found")
    else:
        print(f"❌ {var}: Missing")

print("\n🔧 Checking Twilio configuration...")
for var in twilio_vars:
    if os.getenv(var):
        print(f"✅ {var}: Found")
    else:
        print(f"❌ {var}: Missing")

# Initialize all managers
data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()

# Validate notification manager configuration
notification_config = notification_manager.validate_configuration()
if not notification_config["is_valid"]:
    print(f"⚠️ Notification Manager not fully configured. Missing: {notification_config['missing_fields']}")
    print("SMS notifications will be disabled.")
else:
    print("✅ Notification Manager configured correctly")

# Fetch data from Google Sheet (destinations and their info)
print("\n🌍 Fetching destination data from Google Sheets...")
sheet_data = data_manager.get_destination_data()

if not sheet_data:
    print("❌ No data retrieved from Google Sheets. Check your credentials and endpoint.")
    exit(1)

print(f"📊 Retrieved {len(sheet_data)} destinations")
print("🔍 Sample data structure:")
if sheet_data:
    pprint(sheet_data[0])

# Loop through each destination in the sheet and search for flights from Mexico City (MEX)
print("\n✈️ Searching for flights...")
flight_deals = []  # Store deals to send notifications
updates_made = []  # Store successful updates

for row in sheet_data:
    # Use the exact column names from your Google Sheet
    city = row.get('city', 'Unknown City')  # Column: City
    current_iata = row.get('iataCode', '')  # Column: IATA Code
    current_lowest_price = row.get('lowestPrice', None)  # Column: Lowest Price
    
    print(f"\n🏙️ Processing: {city}")
    print(f"   Current IATA: {current_iata}")
    print(f"   Current lowest price: ${current_lowest_price}")
    
    # If no IATA code exists, try to get it first
    if not current_iata or current_iata == '':
        print(f"   🔍 No IATA code found, looking up for {city}")
        new_iata = flight_search.get_iata_code(city)
        if new_iata:
            row["iataCode"] = new_iata  # This will update the IATA Code column
            current_iata = new_iata
            print(f"   ✅ Found IATA code: {new_iata}")
        else:
            print(f"   ❌ Could not find IATA code for {city}")
            continue
    
    # Search for the cheapest flight from MEX to the destination's IATA code
    print(f"   🔍 Searching flights: MEX → {current_iata}")
    flight = flight_search.search_flights("MEX", current_iata)
    
    if flight and flight.price != "N/A":
        found_price = float(flight.price)
        print(f"   ✅ {city}: ${found_price}, from {flight.origin_airport} to {flight.destination_airport}")
        print(f"      Departure: {flight.out_date} - Return: {flight.return_date}")
        
        # Check if this is a better deal than current lowest price
        should_update = False
        is_deal = False
        
        if current_lowest_price is None or current_lowest_price == "" or current_lowest_price == 0:
            # No previous price, so update with found price
            should_update = True
            print(f"   📊 No previous price recorded, updating with ${found_price}")
        else:
            current_price = float(current_lowest_price)
            if found_price < current_price:
                    # Found a better deal!
                is_deal = True
                should_update = True
                savings = current_price - found_price
                print(f"   🎉 DEAL FOUND! New price ${found_price} is ${savings:.2f} cheaper than ${current_price}")

                # Add to deals list for notification
                flight_deals.append({
                    'city': city,
                    'current_price': current_price,
                    'found_price': found_price,
                    'out_date': flight.out_date,
                    'return_date': flight.return_date,
                    'flight_data': flight
                })

            elif found_price == current_price:
                print(f"   ℹ️ Same price as recorded: ${found_price}")
            else:
                print(f"   📈 Price increased: ${found_price} (was ${current_price})")
        
        # Update the row data if we should
        if should_update:
            row["iataCode"] = flight.destination_airport    # IATA Code column
            row["lowestPrice"] = found_price                # Lowest Price column
            updates_made.append({
                'city': city,
                'price': found_price,
                'is_deal': is_deal
            })
    else:
        # If no flight is found or an error occurred, print N/A for that city
        print(f"   ❌ {city}: No flights found")
        continue

# Send notifications for deals found
if flight_deals and notification_config["is_valid"]:
    print(f"\n📱 Sending notifications for {len(flight_deals)} deals found...")
    
    if len(flight_deals) == 1:
        # Send individual alert for single deal
        deal = flight_deals[0]
        success = notification_manager.send_flight_alert(
            deal['flight_data'],
            deal['city'],
            deal['current_price'],
            deal['found_price']
        )
        if success:
            print("✅ Deal notification sent successfully!")
        else:
            print("❌ Failed to send deal notification")
    else:
        # Send summary alert for multiple deals
        success = notification_manager.send_multiple_alerts(flight_deals)
        if success:
            print("✅ Multiple deals notification sent successfully!")
        else:
            print("❌ Failed to send multiple deals notification")
elif flight_deals and not notification_config["is_valid"]:
    print(f"\n⚠️ {len(flight_deals)} deals found but SMS notifications are disabled due to missing Twilio configuration")
    for deal in flight_deals:
        savings = deal['current_price'] - deal['found_price']
        print(f"   🎉 {deal['city']}: ${deal['found_price']} (save ${savings:.2f})")
else:
    print("\n📊 No deals found this time. All current prices are still the best available.")

# Print the data that will be sent to Sheety
print(f"\n📋 {len(updates_made)} updates to be sent to Google Sheets:")
for update in updates_made:
    deal_indicator = "🎉 DEAL!" if update['is_deal'] else "📊 UPDATE"
    print(f"   {deal_indicator} {update['city']}: ${update['price']}")

# Send changes to Sheety
if updates_made:
    print("\n🔄 Updating Google Sheets...")
    data_manager.update_destination_codes(sheet_data)
else:
    print("\n📊 No updates needed for Google Sheets.")

# Print the updated sheet data for verification/debugging
print("\n📊 Final data:")
pprint(sheet_data)