# Logging Application Start
from narco_crawler import logging

logging.info("program started")

# Grab version from python packaging files
import pkg_resources

global version
version = pkg_resources.require("NarcoCrawler")[0].version

from typing import Optional, Sequence
import argparse
import os
import time
from rich import print as rprint


def arg_conf(args):
    logging.info("Argument Confirmer Called")

    # Wait if wrong input supplied.
    if args.inspect:
        rprint("\t\t[yellow]Input: inspect existing links in the db.[/yellow]")
    if args.build:
        rprint("\t\t[yellow]Input: build images at runtime.[/yellow]")
    if args.crawl:
        rprint("\t\t[yellow]Input: crawl.[/yellow]")

    rprint(
        "\t\t[yellow]If any of these inputs are wrong, you can pause execution now.[/yellow]"
    )

    try:
        time.sleep(2)
    except KeyboardInterrupt:
        logging.warning("Argument Confirmer manually interrupted, application exiting.")
        rprint(f"Exiting now, thank you for using NarcoCrawler(ver:{version}).")
        exit()
    except Exception as e:
        logging.exception(
            f"Exception: {e} occured at argument confirmer point", exc_info=True
        )
        exit()
    finally:
        logging.info("Argument Confirmer Ended")


def main(argv: Optional[Sequence[str]] = None):
    # Clear Screen
    os.system("clear")

    # Argument Parsing
    parser = argparse.ArgumentParser()

    # Parser Arguments
    parser.add_argument(
        "-b",
        "--build",
        help="Run with a -b flag to build images.",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--crawl",
        help="Run with a -c flag to crawl the dark web based on config file.",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--inspect",
        help="Run with a -i flag to inspect the links in the database.",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Set the -v flag to print the version.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Set the -q flag to not print banner",
    )

    # Processing args
    try:
        args = parser.parse_args(argv)
    except Exception as e:
        logging.exception(e, exc_info=True)

    if not args.quiet:
        rprint(
            r"""[white]
		  _____             _     __          __  _       _   _                        _____                    _
		 |  __ \           | |    \ \        / / | |     | \ | |                      / ____|                  | |
		 | |  | | __ _ _ __| | __  \ \  /\  / /__| |__   |  \| | __ _ _ __ ___ ___   | |     _ __ __ ___      _| | ___ _ __
		 | |  | |/ _` | '__| |/ /   \ \/  \/ / _ \ '_ \  | . ` |/ _` | '__/ __/ _ \  | |    | '__/ _` \ \ /\ / / |/ _ \ '__|
		 | |__| | (_| | |  |   <     \  /\  /  __/ |_) | | |\  | (_| | | | (_| (_) | | |____| | | (_| |\ V  V /| |  __/ |
		 |_____/ \__,_|_|  |_|\_\     \/  \/ \___|_.__/  |_| \_|\__,_|_|  \___\___/   \_____|_|  \__,_| \_/\_/ |_|\___|_|


		[/white]"""
        )

    if args.version:
        rprint(f"\t\t[white]Version: {version}[/white]")

    # Wait if wrong input supplied.
    if args.inspect or args.build or args.crawl:
        arg_conf(args)

    # Importing Resources to start backend
    from narco_crawler.backend_handler import (
        initializer,
        de_initializer,
        backend_tester,
    )

    if initializer(args.build):
        # Waiting for tor proxy and load balancer to handshake
        rprint("\t\t[green]Backend has been initialized.[/green]\n")

        rprint("\t\t[green]Waiting for backend to setup.")
        time.sleep(10)

        # Verying if docker is up and running.
        if backend_tester():
            rprint("\t\t[green]Backend infrastructure is functional[/green]")
        else:
            rprint(
                "\t\t[red]Backend infrastructure has failed testing, check logs for more details.[/red]"
            )
    else:
        rprint("\t\t[red]Initialization has failed, check logs for more details.")

    if args.crawl:

        # Initiating Crawler procedures
        from narco_crawler.web_crawler.main import start_crawler, de_init_crawler

        if not start_crawler():
            rprint(
                "\t\t[red]Failed to initialize crawler, check logs for more info.[/red]"
            )
        else:
            rprint("\t\t[green]Successfully initialized crawler.")

        # Crawling Area

        if not de_init_crawler():
            rprint(
                "\t\t[red]Failed to initialize crawler, check logs for more info.[/red]"
            )
        else:
            rprint("\t\t[green]Successfully de-initialized crawler.")

    # Taking down backend infra
    rprint("\n\t\t[green]Taking down backend.[/green]")
    if de_initializer():
        rprint("\t\t[green]Backend is taken down.[/green]")
    else:
        rprint(
            "\t\t[red]Failed to takedown backend infra, check logs for more details.[/red]"
        )

    # Closing Down Messages
    logging.info("Stopping Program Narco_Crawler.")
    rprint("[yellow]\n\t\tThank you for using Narco_Crawler.[/yellow]")
