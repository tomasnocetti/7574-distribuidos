from common.middleware import Middleware

THUMBNAIL_EXCHANGE = 'trending_exchange'
DOWNLOAD_QUEUE = 'download_queue'


class ThumbnailInstanceMiddlware(Middleware):
    def __init__(self, instance_nr) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=THUMBNAIL_EXCHANGE,
                                      exchange_type='direct')

        self.channel.queue_declare(queue=DOWNLOAD_QUEUE)

        result = self.channel.queue_declare(queue='', exclusive=True)

        self.input_queue_name = result.method.queue

        self.channel.queue_bind(
            exchange=THUMBNAIL_EXCHANGE, queue=self.input_queue_name, routing_key=instance_nr)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.input_queue_name, lambda ch, method,
                                                properties, body: callback(body.decode()), True)
        self.channel.start_consuming()

    def send_result_message(self, message):

        super().send_message(DOWNLOAD_QUEUE, message)
