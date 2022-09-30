import logging

from common.message import EndResult1, MessageEnd, Result1, VideoMessage
from common.worker import Worker


class TagUnique(Worker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.items = set()

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Videos')
            end_message = EndResult1()
            self.middleware.send_result_message(end_message.pack())
            return

        video = VideoMessage.decode(message)

        try:
            tags = video.content['tags']
            # print(f'Is funny: {'funny' in tags}')
            item = (video.content['video_id'],
                    video.content['title'], video.content['category'])

            if (tags != None and 'funny' in tags and not item in self.items):
                self.items.add(item)
                end_message = Result1(",".join(item))
                self.middleware.send_result_message(end_message.pack())

                # self.middleware.send_video_message(message)
        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')
