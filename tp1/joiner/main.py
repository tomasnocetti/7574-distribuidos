#!/usr/bin/env python
import logging
import os
from src.joiner import Joiner
from src.middleware import Middleware

from os import listdir
from os.path import isfile, join


def main():

    initialize_log(os.getenv("LOGGING_LEVEL") or 'INFO')

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.info("Jointer starting work")

    # Initialize server and start server loop
    middleware = Middleware()
    worker = Joiner(middleware)

    worker.run()

    logging.info(
        'Bye bye!')


def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


if __name__ == "__main__":
    main()
