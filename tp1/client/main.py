#!/usr/bin/env python
import logging
import os
from src.server_connection import ServerConnection
from src.middleware import Middleware

from os import listdir
from os.path import isfile, join

PATH = './data'

CATEGORY_SUBFIX = '_category_id.json'
DATA_SUBFIX = '_youtube_trending_data.csv'

onlyfiles = [f for f in listdir(PATH) if isfile(join(PATH, f))]

category_files = [item
                  for item in onlyfiles if CATEGORY_SUBFIX in item]

raw_data_files = [item.replace(CATEGORY_SUBFIX, '') for item in category_files]


def main():

    initialize_log(os.getenv("LOGGING_LEVEL") or 'DEBUG')

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.info("Client starting work")

    # Initialize server and start server loop
    middleware = Middleware()
    server = ServerConnection(middleware, PATH, category_files, raw_data_files)

    server.run()

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
