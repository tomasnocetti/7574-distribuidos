import csv
import io
import json
import logging
import os
import signal
from time import sleep
from typing import List
from common.constants import DATA_SUBFIX

from common.message import EndResult1, EndResult2, EndResult3, FileMessage, MessageEnd, MessageStart, Result1, VideoMessage
from common.worker import Worker


class ServerConnection(Worker):
    def __init__(self, middleware, path, category_files, raw_data_files, LINES_BUFFER) -> None:
        super().__init__(middleware)

        self.path = path
        self.category_files = category_files
        self.raw_data_files = raw_data_files
        self.LINES_BUFFER = LINES_BUFFER

        self.results1 = []
        self.results2 = []
        self.results3 = []

        self.finish1 = False
        self.finish2 = False
        self.finish3 = False

    def run(self):
        self.send_categories()

        self.send_processed_csv()

        self.middleware.recv_result_message(self.recv_results)

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

            counter = 0
            with open(os.path.join(self.path, file_name)) as file:
                csv_reader = csv.reader(file, delimiter=',')

                # list to store the names of columns
                list_of_column_names = next(csv_reader)

                while (True):
                    f = io.StringIO()
                    lines = self.get_next_file_slice(
                        f, csv_reader, list_of_column_names)

                    if (lines == 0):
                        break

                    f.seek(0)

                    counter += 1
                    message = FileMessage(file_name, f.read())
                    self.middleware.send_video_message(message.pack())

                logging.info(
                    f'Sending Raw Data File: {file_name}, total: {counter}')

        self.middleware.send_video_message(MessageEnd().pack())

    def get_next_file_slice(self, f, csv_reader, header) -> bool:
        writer = csv.writer(f)
        writer.writerow(header)

        counter = 0
        while (True):
            try:
                el = next(csv_reader)
            except csv.Error:
                continue
            except StopIteration:
                return counter

            writer.writerow(el)
            counter += 1
            # print(counter == int(self.LINES_BUFFER))
            if (counter == int(self.LINES_BUFFER)):
                return counter

    def recv_results(self, message):
        if self.is_end_result(message):
            logging.info(f'Recv All Responses!')
            return

        self.process_result1_message(message)

    def is_end_result(self, message):
        if (EndResult1.is_message(message)):
            self.finish1 = True

            ### Printing Results ###
            logging.info('**** Results1 ****')

            for el in self.results1:
                logging.info(f' * {el}')

        if (EndResult2.is_message(message)):
            self.finish2 = True

        if (EndResult3.is_message(message)):
            self.finish3 = True

        return self.finish1 and self.finish2 and self.finish3

    def process_result1_message(self, message):
        if not Result1.is_message(message):
            return

        message = Result1.decode(message)

        self.results1.append(message.content.split(','))

    def __exit_gracefully(self, *args):
        self.mid
        logging.info(
            'Exiting gracefully')
