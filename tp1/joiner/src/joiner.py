import logging

from common.message import FileMessage, MessageEnd, MessageStart, VideoMessage
from common.worker import Worker
from src.model import CategoryMapper


class Joiner(Worker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)

        self.keep_recv_categories = False
        self.keep_recv_videos = False
        self.categories = CategoryMapper()

    def run(self):
        self.middleware.recv_category_message(self.recv_categories)

    def recv_categories(self, message):
        logging.debug('New category message')

        if not self.keep_recv_categories:
            if MessageStart.is_message(message):
                logging.info(f'Starting Recv Categories')

                self.keep_recv_categories = True

            return

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Categories, recv {self.categories.len()} countries')
            self.keep_recv_categories = False
            self.keep_recv_videos = True
            self.middleware.stop_recv_category_message()

            self.middleware.recv_video_message(self.recv_videos)
            return

        if not FileMessage.is_message(message):
            logging.error(f'Unknown message: {message}')
            return

        file_message = FileMessage.decode(message)

        self.categories.load_category_file(
            file_message.file_name, file_message.file_content)

    def recv_videos(self, message):

        if (not self.keep_recv_videos):
            logging.error(f'Video message should not be received: {message}')
            return

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Videos')

            self.middleware.send_video_message(message)
            # self.keep_recv_videos = False
            # self.middleware.stop_recv_video_message()
            return

        video = VideoMessage.decode(message)

        try:
            category_name = self.categories.map_category(
                video.content['country'], video.content['categoryId'])
            video.content.pop('categoryId')
            video.content['category'] = category_name
            self.middleware.send_video_message(video.pack())
        except KeyError as err:
            logging.debug(f'Invalid key error: {err}')
