import csv
import io
import logging
import os
import uuid

from common.message import EndResult1, EndResult2, EndResult3, FileMessage, MessageEnd, Result1, Result2, Result3, BinaryFile
from common.worker import Worker
from common.utils import uid


class ServerConnection(Worker):
    def __init__(self, middleware, path, category_files, raw_data_files, LINES_BUFFER, thumbnail_path) -> None:
        super().__init__(middleware)

        self.path = path
        self.category_files = category_files
        self.raw_data_files = raw_data_files
        self.LINES_BUFFER = LINES_BUFFER

        self.thumbnail_path = thumbnail_path
        # Check whether the specified path exists or not
        isExist = os.path.exists(self.thumbnail_path)
        if not isExist:
            os.makedirs(self.thumbnail_path)

        # Remove all files in the directory
        for f in os.listdir(self.thumbnail_path):
            os.remove(os.path.join(self.thumbnail_path, f))

        self.results1 = []
        self.results3 = ''

        self.finish1 = False
        self.finish2 = False
        self.finish3 = False

    def run(self):
        self.register()

        self.send_categories()

        self.send_processed_csv()

        self.middleware.recv_result_message(self.recv_results)

    def send_categories(self):
        print(self.client_id)

        for file_name in self.category_files:
            logging.info(f'Sending Category File: {file_name}')

            with open(os.path.join(self.path, file_name)) as file:
                data = file.read()

            message = FileMessage(self.client_id, uid(), file_name, data)

            # We allow ourselves to send all data at once because files are small
            self.middleware.send_category_message(message.pack())

        self.middleware.send_category_message(
            MessageEnd(self.client_id, uid()).pack())

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
                    message = FileMessage(
                        self.client_id, uid(), file_name, f.read())
                    self.middleware.send_video_message(message.pack())

                logging.info(
                    f'Sending Raw Data File: {file_name}')

        self.middleware.send_video_message(
            MessageEnd(self.client_id, uid()).pack())

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
            self.exit_gracefully()
            return

        self.process_result1_message(message)
        self.process_result2_message(message)
        self.process_result3_message(message)

    def is_end_result(self, message):
        if (EndResult1.is_message(message)):
            self.finish1 = True

            ### Printing Results ###
            logging.info('**** Results1 ****')

            for el in self.results1:
                logging.info(f' * {el}')

        if (EndResult2.is_message(message)):
            self.finish2 = True
            logging.info('**** Results2 ****')
            logging.info(
                f' * All files downloaded to path: {self.thumbnail_path}')

        if (EndResult3.is_message(message)):
            self.finish3 = True

            ### Printing Results ###
            logging.info('**** Results3 ****')

            logging.info(f' * Top views happened: {self.results3}')

        return self.finish1 and self.finish2 and self.finish3

    def process_result1_message(self, message):
        if not Result1.is_message(message):
            return

        message = Result1.decode(message)

        self.results1.append(message.content.split(','))

    def process_result2_message(self, message):
        if not Result2.is_message(message):
            return

        message = Result2.decode(message)
        binary_chunk = BinaryFile.decode(message.content)

        with open(f'{self.thumbnail_path}/{binary_chunk.file_name}', 'ab+') as file:
            file.write(binary_chunk.file_content)

    def process_result3_message(self, message):
        if not Result3.is_message(message):
            return

        message = Result3.decode(message)

        self.results3 = message.content

    '''
        Blocking method to allow client to start processing
    '''

    def register(self):
        self.client_id = uuid.uuid4().hex
