from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class NotificationManager:
    """
    This class is responsible for sending notifications via SMS using the Twilio API.
    It sends alerts when cheaper flights are found.
    """

    def __init__(self):
        """
        Initializes the NotificationManager with Twilio credentials from environment variables.
        """
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.recipient_phone_number = os.getenv("TWILIO_TO_NUMBER")
        
        # Initialize Twilio client
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            print("✅ Twilio client initialized successfully")
        else:
            print("❌ Twilio credentials not found in environment variables")
            self.client = None

    def send_sms(self, message_body):
        """
        Sends an SMS message using Twilio API.

        Args:
            message_body (str): The message content to send.

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        if not self.client:
            print("❌ Cannot send SMS: Twilio client not initialized")
            return False

        if not self.recipient_phone_number:
            print("❌ Cannot send SMS: Recipient phone number not configured")
            return False

        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.twilio_phone_number,
                to=self.recipient_phone_number
            )
            print(f"✅ SMS sent successfully! Message SID: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Failed to send SMS: {e}")
            return False

    def send_flight_alert(self, flight_data, destination_city, current_price, found_price):
        """
        Sends a flight deal alert SMS with flight booking information.

        Args:
            flight_data: FlightData object containing flight details
            destination_city (str): Name of the destination city
            current_price (str/float): Current lowest price in the sheet
            found_price (str/float): New lower price found

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        # Format the message with flight details
        message = f"🎉 ¡OFERTA DE VUELO ENCONTRADA! 🎉\n\n"
        message += f"Destino: {destination_city}\n"
        message += f"Precio anterior: ${current_price} MXN\n"
        message += f"Nuevo precio: ${found_price} MXN\n"
        message += f"¡Ahorras: ${float(current_price) - float(found_price):.2f} MXN!\n\n"
        message += f"📍 Ruta: {flight_data.origin_airport} → {flight_data.destination_airport}\n"
        message += f"📅 Salida: {flight_data.out_date}\n"
        message += f"📅 Regreso: {flight_data.return_date}\n\n"
        message += f"💡 Reserva pronto antes de que suban los precios!\n"
        message += f"🔗 Busca en Google Flights: MEX to {flight_data.destination_airport}"

        return self.send_sms(message)

    def send_multiple_alerts(self, flight_deals):
        """
        Sends multiple flight deal alerts in a single SMS.

        Args:
            flight_deals (list): List of dictionaries containing flight deal information

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        if not flight_deals:
            return False

        message = f"🎉 ¡{len(flight_deals)} OFERTAS DE VUELO ENCONTRADAS! 🎉\n\n"
        
        for i, deal in enumerate(flight_deals, 1):
            savings = float(deal['current_price']) - float(deal['found_price'])
            message += f"{i}. {deal['city']}\n"
            message += f"   💰 ${deal['found_price']} MXN (ahorro: ${savings:.2f})\n"
            message += f"   📅 {deal['out_date']} - {deal['return_date']}\n\n"

        message += "💡 ¡Reserva pronto antes de que suban los precios!"
        
        return self.send_sms(message)

    def test_connection(self):
        """
        Tests the Twilio connection by sending a test message.

        Returns:
            bool: True if test message was sent successfully, False otherwise.
        """
        test_message = "🧪 Mensaje de prueba del Flight Deal Finder - Twilio funcionando correctamente!"
        return self.send_sms(test_message)

    def validate_configuration(self):
        """
        Validates that all required Twilio configuration is present.

        Returns:
            dict: Dictionary with validation results and missing fields.
        """
        missing_fields = []
        
        if not self.account_sid:
            missing_fields.append("TWILIO_ACCOUNT_SID")
        if not self.auth_token:
            missing_fields.append("TWILIO_AUTH_TOKEN")
        if not self.twilio_phone_number:
            missing_fields.append("TWILIO_PHONE_NUMBER")
        if not self.recipient_phone_number:
            missing_fields.append("TWILIO_TO_NUMBER")

        return {
            "is_valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "client_initialized": self.client is not None
        }

# Test to verify if the message is sent from twilio
# if __name__ == "__main__":
#     notifier = NotificationManager()
#     result = notifier.send_sms("🧪 Test message from José's flight alert app!")
#     print("Message sent:", result)