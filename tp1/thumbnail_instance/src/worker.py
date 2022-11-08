import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import CategoryMessage, MessageEnd, VideoMessage
from datetime import datetime
from .model import ThumbnailGrouper


class ThumbnailInstance(HeartbeathedWorker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.processed = []
        self.dir = f'.temp'
        self.grouper = ThumbnailGrouper(self.dir)
        self.counter = 0
        self.category_count = 0

    def run(self):
        self.middleware.recv_category_count(self.recv_category_count)
        self.middleware.recv_video_message(self.recv_videos)

    def recv_category_count(self, message):
        if CategoryMessage.is_message(message):
            message = CategoryMessage.decode(message)

            self.category_count = int(message.content)

            self.middleware.stop_recv_category_count()
            logging.info(
                f'Finish Recv Category Count: {message.content}')

            return

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Videos')
            self.middleware.send_result_message(message)
            self.restore()
            return

        video = VideoMessage.decode(message)
        try:

            video_id = video.content['video_id']
            country = video.content['country']

            trending_date = datetime.strptime(
                video.content['trending_date'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d")

            completed = self.grouper.add_date(video_id, country, trending_date)

            if (completed and not video_id in self.processed):
                self.processed.append(video_id)
                self.middleware.send_result_message(message)

                logging.info(
                    f'Tenemos 21 y 11 paises: {video_id}')
                return

        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')

    def restore(self):
        self.grouper = ThumbnailGrouper(self.dir)
        self.processed = []
