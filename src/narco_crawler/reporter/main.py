from narco_crawler.config.db import database
from narco_crawler.config.config import config
from narco_crawler.reporter import reporter_logger as logging

def report_drugs():
	logging.info("Reported drugs")
	try:
		emails = config["emails"]
	except KeyError:
		logging.critical("No emails found in config file, please fix or atleast leave a blank string.")
		return False
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
