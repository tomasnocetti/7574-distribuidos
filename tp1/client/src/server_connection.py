import logging
import os
import signal
from time import sleep

from common.message import FileMessage, FileMessageEnd, FileMessageStart
from .middleware import Middleware


class ServerConnection():
    def __init__(self, middleware, path, category_files, raw_data_files) -> None:
        self.running = True
        signal.signal(signal.SIGTERM, self.__exit_gracefully)
        signal.signal(signal.SIGINT, self.__exit_gracefully)

        self.middleware: Middleware = middleware
        self.path = path
        self.category_files = category_files
        self.raw_data_files = raw_data_files

    def run(self):
        self.send_categories()

        while(self.running):
            sleep(2)

    def send_categories(self):
        self.middleware.send_category_message(FileMessageStart().pack())

        for file_name in self.category_files:
            logging.info(f'Sending Category File: {file_name}')

            with open(os.path.join(self.path, file_name)) as file:
                data = file.read()

            message = FileMessage(file_name, data)

            # We allow ourselves to send all data at once because files are small
            self.middleware.send_category_message(message.pack())

        self.middleware.send_category_message(FileMessageEnd().pack())

    def __exit_gracefully(self, *args):
        self.running = False
        logging.info(
            'Exiting gracefully')
