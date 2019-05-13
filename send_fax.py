import os
from twilio.rest import Client


account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

from_number = "+18728147688"
to_number = "+13182599773"

media_url = (
    # "https://s3.amazonaws.com/accurate-replica-001/Jackson+Parish+Clearance+request.pdf"
    "https://s3.amazonaws.com/accurate-replica-001/7b200b52-7318-46a0-814a-d6ec606bd7c5.pdf"
)

fax = client.fax.faxes.create(from_=from_number, to=to_number, media_url=media_url)

print(fax.sid)
