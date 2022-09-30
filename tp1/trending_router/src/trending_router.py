import logging

from common.message import MessageEnd, VideoMessage
from common.worker import Worker


class TrendingRouter(Worker):
    def __init__(self, middleware, instances) -> None:
        super().__init__(middleware)
        self.nr_instances = instances

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Videos')

            self.middleware.send_video_message(message)
            return

        video = VideoMessage.decode(message)

        try:
            if (video.content['trending_date'] != None):
                print(video.content['trending_date'], self.get_instance_n(
                    video.content['trending_date']))
                self.middleware.send_video_message(message)
        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')

    def get_instance_n(self, key):
        return hash(key) % self.nr_instances
