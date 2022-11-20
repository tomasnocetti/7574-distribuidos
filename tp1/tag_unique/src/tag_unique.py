import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import EndResult1, MessageEnd, Result1, VideoMessage


class TagUnique(HeartbeathedWorker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.items = set()

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Videos')
            parsed_message = MessageEnd.decode(message)
            end_message = EndResult1(parsed_message.client_id, '1')
            self.middleware.send_result_message(end_message.pack())
            return

        video = VideoMessage.decode(message)

        try:
            tags = video.content['tags']
            # print(f'Is funny: {'funny' in tags}')
            item = (video.content['video_id'],
                    video.content['title'], video.content['category'])

            logging.info(item)
            if (tags != None and 'funny' in tags and not item in self.items):
                self.items.add(item)
                end_message = Result1(video.client_id, video.message_id, ",".join(item))
                self.middleware.send_result_message(end_message.pack())

                # self.middleware.send_video_message(message)
        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')
