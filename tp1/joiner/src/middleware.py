from common.middleware import Middleware

RAW_DATA_QUEUE = 'raw_data_queue'
CATEGORIES_QUEUE = 'categories_queue'
VIDEO_DATA_QUEUE = 'video_data'


class JoinerMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.raw_data_queue = self.channel.queue_declare(queue=RAW_DATA_QUEUE)
        self.categories_queue = self.channel.queue_declare(
            queue=CATEGORIES_QUEUE)
        self.input_videos_queue = self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE)

    def stop_recv_category_message(self):
        super().stop_recv_message(self.cat_msg_tag)

    def recv_category_message(self, callback):
        self.cat_msg_tag = super().recv_message(CATEGORIES_QUEUE, lambda ch, method,
                                                properties, body: callback(body.decode()))

        self.channel.start_consuming()

    def recv_video_message(self, callback):

        self.cat_msg_tag = super().recv_message(VIDEO_DATA_QUEUE, lambda ch, method,
                                                properties, body: callback(body.decode()))
