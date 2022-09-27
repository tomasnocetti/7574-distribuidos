import csv
from io import StringIO
import logging
from time import sleep

from common.message import FileMessage, MessageEnd, VideoMessage
from common.worker import Worker
from common.constants import DATA_SUBFIX


class Dropper(Worker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):
        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Video Files')
            return

        if not FileMessage.is_message(message):
            logging.error(f'Unknown message: {message}')
            return

        file_message = FileMessage.decode(message)

        country = file_message.file_name.replace(DATA_SUBFIX, '')

        fields = ['video_id', 'title', 'categoryId',
                  'likes', 'trending_date', 'thumbnail_link']

        f = StringIO(file_message.file_content)
        reader = csv.DictReader(f)
        sleep(1)
        for row in reader:
            dropped = {your_key: row[your_key]
                       for your_key in fields}
            dropped['country'] = country
            logging.info(f'Proccessed message: {dropped}')
            message = VideoMessage(dropped)
            self.middleware.send_video_message(message.pack())
