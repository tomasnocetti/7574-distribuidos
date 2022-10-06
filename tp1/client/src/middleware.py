from common.middleware import Middleware

CATEGORIES_EXCHANGE = 'categories_exchange'
DROPPER_INPUT_QUEUE = 'dropper_input'
RESULTS_QUEUE = 'results_queue'


class ClientMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.exchange_declare(exchange=CATEGORIES_EXCHANGE,
                                      exchange_type='fanout')
        self.channel.queue_declare(
            queue=DROPPER_INPUT_QUEUE)

        self.channel.queue_declare(
            queue=RESULTS_QUEUE)

    def send_category_message(self, message):
        super().send_to_exchange(CATEGORIES_EXCHANGE, '', message)

    def send_video_message(self, message):
        super().send_message(DROPPER_INPUT_QUEUE, message)

    def recv_result_message(self, callback):
        super().recv_message(RESULTS_QUEUE, lambda ch, method,
                             properties, body: callback(body.decode()), True)
        self.channel.start_consuming()
