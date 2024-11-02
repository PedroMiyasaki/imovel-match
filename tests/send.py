# Import os and dotenv
import os
from dotenv import load_dotenv
load_dotenv()

# Import twilio client
from twilio.rest import Client

# Create the client
client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

# Send the message to test Twilio API
client.messages.create(body="foo", from_='whatsapp:+14155238886', to='whatsapp:' + os.environ["CANVAS_PHONE_NUMBER"])
