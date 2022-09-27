import csv
import json
import logging
import os
import signal
from time import sleep
from common.constants import DATA_SUBFIX

from common.message import FileMessage, MessageEnd, MessageStart, VideoMessage

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

        self.send_processed_csv()

    def send_categories(self):
        self.middleware.send_category_message(MessageStart().pack())

        for file_name in self.category_files:
            logging.info(f'Sending Category File: {file_name}')

            with open(os.path.join(self.path, file_name)) as file:
                data = file.read()

            message = FileMessage(file_name, data)

            # We allow ourselves to send all data at once because files are small
            self.middleware.send_category_message(message.pack())

        self.middleware.send_category_message(MessageEnd().pack())

    '''
    /** Move this logic to dropper **/
    '''

    def send_processed_csv(self):
        for file_name in self.raw_data_files:
            logging.info(f'Sending Raw Data File: {file_name}')

            with open(os.path.join(self.path, file_name)) as file:
                country = file_name.replace(DATA_SUBFIX, '')

                fields = ['video_id', 'title', 'categoryId',
                          'likes', 'trending_date', 'thumbnail_link']

                reader = csv.DictReader(file)
                for row in reader:
                    dropped = {your_key: row[your_key]
                               for your_key in fields}
                    dropped['country'] = country
                    message = VideoMessage(dropped)

                    self.middleware.send_video_message(message.pack())

            # We allow ourselves to send all data at once because files are small

    def __exit_gracefully(self, *args):
        self.running = False
        logging.info(
            'Exiting gracefully')
