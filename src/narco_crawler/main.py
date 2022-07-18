# Logging Application Start
from narco_crawler import logging
from narco_crawler.config.config import maxcores

logging.info("NarcoCrawler started")

# Importing Resources to start backend
from narco_crawler.infrahandler.main import (
    initializer,
    de_initializer,
)

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
    rprint("\n\t[white]Confirm Arguments[/white]")
    if args.build:
        rprint("\t\t[yellow]Input: build images at runtime.[/yellow]")
    if args.crawl:
        rprint("\t\t[yellow]Input: crawl.[/yellow]")
    if args.skip_down:
        rprint(
            "\t\t[yellow]Input: Cancel infrastructure takedown, not recommended.[/yellow]"
        )
    if args.skip_tests:
        rprint(
            "\t\t[yellow]Input: Skip infra testing.[/yellow]"
        )
    if args.spider:
        rprint(
            "\t\t[yellow]Input: Spider website[/yellow]"
        )

    rprint(
        "\t\t[yellow]If any of these inputs are wrong, you can pause execution now.[/yellow]"
    )

    try:
        time.sleep(2)
    except KeyboardInterrupt:
        logging.warning("Argument Confirmer manually interrupted, application exiting.")
        rprint(f"\t\tExiting now, thank you for using NarcoCrawler(ver:{version}).")
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
        "--info",
        help="Run with a --process to get process no.",
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
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Set the --skip-tests flag to not print banner",
    )
    parser.add_argument(
        "--skip-down",
        action="store_true",
        help="Set the --skip-down flag to not print banner",
    )
    parser.add_argument(
        "--spider",
        action="store_true",
        help="Run with spider markets flag to scan all active markets and spider on a deeper level",
    )

    # Processing args
    try:
        args = parser.parse_args(argv)
    except Exception as e:
        logging.exception(e, exc_info=True)

    if not args.quiet:
        print(
            r"""
          _____             _     __          __  _       _   _                        _____                    _
         |  __ \           | |    \ \        / / | |     | \ | |                      / ____|                  | |
         | |  | | __ _ _ __| | __  \ \  /\  / /__| |__   |  \| | __ _ _ __ ___ ___   | |     _ __ __ ___      _| | ___ _ __
         | |  | |/ _` | '__| |/ /   \ \/  \/ / _ \ '_ \  | . ` |/ _` | '__/ __/ _ \  | |    | '__/ _` \ \ /\ / / |/ _ \ '__|
         | |__| | (_| | |  |   <     \  /\  /  __/ |_) | | |\  | (_| | | | (_| (_) | | |____| | | (_| |\ V  V /| |  __/ |
         |_____/ \__,_|_|  |_|\_\     \/  \/ \___|_.__/  |_| \_|\__,_|_|  \___\___/   \_____|_|  \__,_| \_/\_/ |_|\___|_|


        """
        )

    if args.info:
        rprint(f"[green]\tProcess Number: { os.getpid() }[/green]")
        rprint(f"[green]\tMaximum Cores: { maxcores() }[/green]")
        os.system(f"echo { os.getpid() } | xclip -sel clip")

    if args.version:
        rprint(f"\t\t[white]Version: {version}[/white]")

    # Wait if wrong input supplied.
    if args.inspect or args.build or args.crawl or args.skip_down:
        arg_conf(args)

    rprint("\n\t[white]Initialization[/white]")
    logging.info("Starting Infra")
    try:
        if initializer(args.build, args.skip_tests):
            # Waiting for tor proxy and load balancer to loophandshake
            rprint("\t\t[green]Backend has been initialized.[/green]")
            logging.info("Successfully started Infra")
        else:
            rprint(
                "\t\t[red]Initialization of infra has failed, check logs/infra.log for more details."
            )
            logging.critical(
                "Failed to start info, check logs/infra.log for more details."
            )
    except KeyboardInterrupt:
        rprint("\t      [red]Initialization manually interrupted, terminating.[/red]")
        logging.warning(
            "Initialization manually terminated, taking down infrastructure."
        )
        args.spider = False
        args.crawl = False
        args.skip_down = False

    if args.crawl:
        rprint("[white]\n\tCrawler[/white]")
        logging.info("Crawler started")
        # Initiating Crawler procedures
        from narco_crawler.crawler.main import (
            run_crawler,
        )
        from narco_crawler.ingress.main import ingress_main

        rprint("[green]\t\tAttempting to run crawler with config files.[/green]")
        if not run_crawler():
            try:
                rprint(
                    "\t\t[red]Failed to successfully capture all links, inspect 'engines.log' for detailed info.[/red]"
                )
            except KeyboardInterrupt:
                rprint("Crawler manually interrupted, terminating.")
                logging.warning(
                    "Crawler manually terminated, taking down infrastructure."
                )
        else:
            rprint("\t\t[green]Successfully ran crawler.[/green]")

        # Ingress Crawl
        rprint("[white]\n\tIngress[/white]")
        rprint("[green]\t\tIngressing[/green]")
        if not ingress_main():
            try:
                rprint(
                    "\t\t[red]Failed to successfully ingress all links, inspect 'ingress.log' for detailed info.[/red]"
                )
            except KeyboardInterrupt:
                rprint("Ingress manually interrupted, terminating.")
                logging.warning(
                    "Ingress manually terminated, taking down infrastructure."
                )
        else:
            rprint("\t\t[green]Successfully ran ingress.[/green]")

        rprint("\n\t[white]Validator[/white]")
        logging.info("Starting validator, for dormant and drug relevant links.")
        from narco_crawler.validator.main import validator_base

        if validator_base():
            rprint("\t\t[green]Validator finished, run successful[/green]")
            logging.info("Finished validator base run.")
        else:
            rprint("\t\t[red]Validator failed, check logs/validator.log for more details[/red]")
            logging.warning("Finished validator base run, unsuccessful")

        if args.spider:
            rprint("[white]\n\tSpider[/white]")
            logging.info("Spider started")

            from narco_crawler.spider.main import spider

            rprint("[green]\t\tSpidering all links[/green]")
            if not spider():
                try:
                    rprint(
                        "\t\t[red]Failed to successfully spider all links, inspect 'spider.log' for detailed info.[/red]"
                    )
                except KeyboardInterrupt:
                    rprint("Spider manually interrupted, terminating.")
                    logging.warning(
                        "Spider manually terminated, taking down infrastructure."
                    )
            else:
                rprint("\t\t[green]Successfully ran Spider.[/green]")

        rprint("[green]\n\tValidator Secondary Run[/green]")
        logging.info("Validator Secondary Run")
        from narco_crawler.validator.main import validator_primary
        if validator_primary():
            rprint("\t\t[green]Validator Second finished, run successful[/green]")
            logging.info("Finished validator second run.")
        else:
            rprint("\t\t[red]Validator Second run failed, check logs/validator.log for more details[/red]")
            logging.warning("Finished validator secondary run, unsuccessful")

        from narco_crawler.sorter.main import sorter
        rprint("\n\t[white]Sorter[/white]")
        if sorter():
            rprint("\t\tSorter run successful, calling reporter now")
            logging.info("[green]Sorter run successful, calling reporter now[/green]")
        else:
            rprint("\t\tSorter run unsuccessful, calling reporter now")
            logging.info("[green]Sorter run unsuccessful, calling reporter now[/green]")

        rprint("\n\t[white]Reporter[/white]")
        logging.info("Reporter called")
        from narco_crawler.reporter.main import reporter_main
        if reporter_main():
            rprint("[green]\t\tReported results, shutting down now.")
            logging.info("Reporter finished")
        else:
            rprint("[red]\t\tFailed to run reporter, this is not good[/red]")
            logging.critical("Reporter failed, view logs/reporter.log for more details.")


    # Taking down backend infra
    rprint("\n\t[white]De-Initialization[/white]")
    if not args.skip_down:
        logging.info("Stopping Infra")
        rprint("\t\t[green]Taking down backend.[/green]")
        if de_initializer():
            rprint("\t\t[green]Backend is taken down.[/green]")
            logging.info("Successfully stopped infra")
        else:
            rprint(
                "\t\t[red]De-Initialization of infra has failed, check logs/infra.log for more details."
            )
            logging.critical(
                "Failed to takedown infrastructure, check logs/infra.log for more."
            )
    else:
        rprint(
            "[red]\t\tLeaving Backend Infrastructure running(user input), not recommended.[/red]"
        )

    # Closing Down Messages
    logging.info("NarcoCrawler stopped")
    rprint("[yellow]\n\tThank you for using Narco_Crawler.[/yellow]")
