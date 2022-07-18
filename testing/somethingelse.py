"""
This call sends a message to one recipient.
"""
from mailjet_rest import Client
import os
api_key = "134edf65a45492ee7907da25952a9002"
api_secret = "e02f408a447b89100bde82649ae0ee07"
mailjet = Client(auth=(api_key, api_secret))
data = {
	'FromEmail': 'reporting@mustansirg.in',
	'FromName': 'Narco Crawler',
	'Subject': 'Your email flight plan!',
	'Text-part': 'Dear passenger, welcome to Mailjet! May the delivery force be with you!',
	'Html-part': '<h3>Dear passenger, welcome to <a href=\"https://www.mailjet.com/\">Mailjet</a>!<br />May the delivery force be with you!',
	'Recipients': [{'Email':'me@mustansirg.in'}]
}
result = mailjet.send.create(data=data)
print(result.status_code)
print(result.json())			