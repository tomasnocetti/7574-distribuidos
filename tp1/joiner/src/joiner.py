import logging
from common.heartbeathed_worker import HeartbeathedWorker
from common.message import CategoryMessage, FileMessage, MessageEnd, VideoMessage, BaseMessage
from src.model import CategoryMapper


class Joiner(HeartbeathedWorker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)

        self.categories = CategoryMapper()

    def run(self):
        self.middleware.recv_category_message(self.recv_categories)
        self.middleware.recv_video_message(self.recv_videos)

    def recv_categories(self, message):
        logging.info('New category message')

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Categories, recv {self.categories.len()} countries')
            parsed_message = MessageEnd.decode(message)
            message = CategoryMessage(parsed_message.client_id, self.categories.len())
            self.middleware.send_category_count(message.pack())

            self.middleware.stop_recv_category_message()
            return

        if not FileMessage.is_message(message):
            logging.error(f'Unknown message: {message}')
            return

        file_message = FileMessage.decode(message)

        self.categories.load_category_file(
            file_message.file_name, file_message.file_content)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Videos')

            self.middleware.send_video_message(message)

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

    def category_len(self):
        len(self.categories)
