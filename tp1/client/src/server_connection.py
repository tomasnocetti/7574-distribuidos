import csv
import io
import json
import logging
import os
import signal
from time import sleep
from common.constants import DATA_SUBFIX

from common.message import FileMessage, MessageEnd, MessageStart, VideoMessage

from .middleware import Middleware


class ServerConnection():
    def __init__(self, middleware, path, category_files, raw_data_files, LINES_BUFFER) -> None:
        self.running = True
        signal.signal(signal.SIGTERM, self.__exit_gracefully)
        signal.signal(signal.SIGINT, self.__exit_gracefully)

        self.middleware: Middleware = middleware
        self.path = path
        self.category_files = category_files
        self.raw_data_files = raw_data_files
        self.LINES_BUFFER = LINES_BUFFER

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

    def send_processed_csv(self):
        for file_name in self.raw_data_files:
            logging.info(f'Sending Raw Data File: {file_name}')

            with open(os.path.join(self.path, file_name)) as file:
                csv_reader = csv.reader(file, delimiter=',')

                # list to store the names of columns
                list_of_column_names = next(csv_reader)
                keep_iterating = True

                while(keep_iterating):
                    f = io.StringIO()
                    keep_iterating = self.get_next_file_slice(
                        f, csv_reader, list_of_column_names)
                    f.seek(0)

                    message = FileMessage(file_name, f.read())
                    self.middleware.send_video_message(message.pack())

    def get_next_file_slice(self, f, csv_reader, header) -> bool:
        writer = csv.writer(f)
        writer.writerow(header)

        counter = 0
        for el in csv_reader:
            if(counter == self.LINES_BUFFER):
                return True

            writer.writerow(el)
            counter += 1

        return False

    def __exit_gracefully(self, *args):
        self.running = False
        logging.info(
            'Exiting gracefully')
