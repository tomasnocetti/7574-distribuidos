import csv
from io import StringIO
import logging

from common.message import FileMessage, MessageEnd, VideoMessage
from common.heartbeathed_worker import HeartbeathedWorker
from common.constants import DATA_SUBFIX


class Dropper(HeartbeathedWorker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):
        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Video Files')
            self.middleware.send_video_message(message)
            return

        if not FileMessage.is_message(message):
            logging.error(f'Unknown message: {message}')
            return

        file_message = FileMessage.decode(message)

        country = file_message.file_name.replace(DATA_SUBFIX, '')

        fields = ['video_id', 'title', 'categoryId',
                  'likes', 'trending_date', 'thumbnail_link', 'tags', 'view_count']

        f = StringIO(file_message.file_content)
        reader = csv.DictReader(f)

        for row in reader:
            dropped = {your_key: row[your_key]
                       for your_key in fields}
            dropped['country'] = country
            logging.debug(f'Proccessed message: {dropped}')
            message = VideoMessage(dropped)
            self.middleware.send_video_message(message.pack())

        f.close()
        # self.middleware.send_video_message(message.pack())
        # f.close()
