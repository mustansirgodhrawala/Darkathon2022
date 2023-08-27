from datetime import date
from narco_crawler.config.db import database
from narco_crawler.config.config import config
from narco_crawler.reporter import reporter_logger as logging
from mailjet_rest import Client
import os
import time 

def report_drugs():
	logging.info("Reported drugs")
	try:
		emails = config["emails"]
	except KeyError:
		logging.critical("No emails found in config file, please fix or atleast leave a blank string.")
		return False
	cursor = database.cursor()
	cursor.execute("SELECT * FROM drug_india_sites;")
	links = cursor.fetchall()

	for email in emails:
		send_email(links, email)

	return True

def send_email(links,email):
	today = date.today()
	api_key = "apikey"
	api_secret = "apisecret"
	mailjet = Client(auth=(api_key, api_secret))
	data = {
		'FromEmail': 'reporting@mustansirg.in',
		'FromName': 'Narco Crawler',
		'Subject': f'Results for {today}',
		'Text-part': f'Today, we have for you {len(links)} as many links, here they are \n {links}',
		'Recipients': [{'Email':email}]
	}
	result = mailjet.send.create(data=data)
	return True

def reporter_main():
	logging.info("Reporter initiated")
	try:
		report_drugs()
	except Exception as e:
		logging.critical("Failed to report drugs")
		logging.exception(e, exc_info=True)
		return False
	finally:
		return True
