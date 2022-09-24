import logging
import signal
from time import sleep

from .middleware import Middleware


class Joiner():
    def __init__(self, middleware) -> None:
        self.running = True
        signal.signal(signal.SIGTERM, self.__exit_gracefully)
        signal.signal(signal.SIGINT, self.__exit_gracefully)

        self.middleware: Middleware = middleware

    def run(self):
        self.middleware.recv_category_message(self.recv_categories)

        while (self.running):
            sleep(2)

    def recv_categories(self, message):
        logging.info(f'Reciving message: {message}')

        # self.middleware.recv_c(FileMessageStart().pack())

        # for file_name in self.category_files:

        #     with open(os.path.join(self.path, file_name)) as file:
        #         data = file.read()

        #     message = FileMessage(file_name, data)

        #     # We allow ourselves to send all data at once because files are small
        #     self.middleware.send_category_message(message.pack())

        # self.middleware.send_category_message(FileMessageEnd().pack())

    def __exit_gracefully(self, *args):
        self.running = False
        logging.info(
            'Exiting gracefully')
