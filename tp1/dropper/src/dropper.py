import csv
import logging

from common.message import FileMessage, MessageEnd, VideoMessage
from common.worker import Worker
from common.constants import DATA_SUBFIX


class Dropper(Worker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):
        logging.info('New video message')

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

        reader = csv.DictReader(file_message.file_content)
        for row in reader:
            dropped = {your_key: row[your_key]
                       for your_key in fields}
            dropped['country'] = country
            message = VideoMessage(dropped)

            self.middleware.send_video_message(message.pack())

        print(file_message.content)
