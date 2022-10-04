from common.middleware import Middleware

RESULTS_QUEUE = 'results_queue'
DOWNLOAD_QUEUE = 'download_queue'


class DownloaderMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()

        self.channel.queue_declare(queue=DOWNLOAD_QUEUE)
        self.channel.queue_declare(queue=RESULTS_QUEUE)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(DOWNLOAD_QUEUE, lambda ch, method,
                                                properties, body: callback(body.decode()), True)
        self.channel.start_consuming()

    def send_result_message(self, message):

        super().send_message(RESULTS_QUEUE, message)
