from common.middleware import Middleware

DROPPER_INPUT_QUEUE = 'dropper_input'
VIDEO_DATA_QUEUE = 'video_data'


class DropperMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.queue_declare(
            queue=DROPPER_INPUT_QUEUE)

        self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(DROPPER_INPUT_QUEUE, lambda ch, method,
                                                properties, body: callback(body.decode()))

    def send_video_message(self, message):
        super().send_message(VIDEO_DATA_QUEUE, message)
