from typing import Optional, Sequence
import argparse
import os
import time
from rich import print as rprint
import json

def main():	
	rprint("[green]Welcome to narco_config, locating config file now.")
	
	# Try to get file
	try:
		file = os.environ.get("config_file")
		rprint("[green]Config file found, parsing now")
	except:
		rprint("[red]Could not find config_file, please add to env variables")

	if not file is None:
		with open(str(file),"r") as f:
			data = json.loads(f.read())
	else:
		rprint("[red]Env variable is not set, exiting[/red]")
		exit()

	while True:
		rprint("[white]Options:[/white]")
		rprint("[white]\t1. Add topic.")
		rprint("[white]\t2. Delete topic.")
		rprint("[white]\t3. Add keyword.")
		rprint("[white]\t4. Delete keyword.")
		rprint("[white]\t5. Set New Database Creds.")
		try:
			choice = int(input("Choose an option: "))
		except:
			rprint("Choose a valid option")