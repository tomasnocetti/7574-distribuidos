from common.middleware import Middleware

CATEGORIES_QUEUE = 'categories_queue'
DROPPER_INPUT_QUEUE = 'dropper_input'


class ClientMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.queue_declare(
            queue=CATEGORIES_QUEUE)
        self.channel.queue_declare(
            queue=DROPPER_INPUT_QUEUE)

    def send_category_message(self, message):
        super().send_message(CATEGORIES_QUEUE, message)

    def send_video_message(self, message):
        super().send_message(DROPPER_INPUT_QUEUE, message)
