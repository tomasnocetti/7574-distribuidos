from common.middleware import Middleware

CATEGORIES_COUNT_EXCHANGE = 'categories_count_exchange'
THUMBNAIL_EXCHANGE = 'thumbnail_exchange'
DOWNLOAD_QUEUE = 'download_queue'


class ThumbnailInstanceMiddlware(Middleware):
    def __init__(self, instance_nr) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=THUMBNAIL_EXCHANGE,
                                      exchange_type='direct')

        self.channel.exchange_declare(exchange=CATEGORIES_COUNT_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.queue_declare(queue=DOWNLOAD_QUEUE)

        result = self.channel.queue_declare(queue='', exclusive=True)

        self.input_queue_name = result.method.queue

        self.channel.queue_bind(
            exchange=THUMBNAIL_EXCHANGE, queue=self.input_queue_name, routing_key=instance_nr)

    def recv_category_count(self, callback):
        category_count = self.channel.queue_declare(
            queue='', auto_delete=True)

        self.channel.queue_bind(
            exchange=CATEGORIES_COUNT_EXCHANGE, queue=category_count.method.queue, routing_key='')

        self.cat_count_tag = super().recv_message(category_count.method.queue, lambda ch, method,
                                                  properties, body: callback(body.decode()), True)
        self.channel.start_consuming()

    def stop_recv_category_count(self):
        super().stop_recv_message(consumer_tag=self.cat_count_tag)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.input_queue_name, lambda ch, method,
                                                properties, body: callback(body.decode()), True)

        self.channel.start_consuming()

    def send_result_message(self, message):

        super().send_message(DOWNLOAD_QUEUE, message)
