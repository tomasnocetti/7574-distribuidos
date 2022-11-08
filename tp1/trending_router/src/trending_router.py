import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import MessageEnd, VideoMessage


class TrendingRouter(HeartbeathedWorker):
    def __init__(self, middleware, instances) -> None:
        super().__init__(middleware)
        self.nr_instances = instances

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):

            for id in range(self.nr_instances):
                logging.info(
                    f'Finish Recv Videos, message to instance: {id}')
                self.middleware.send_video_message(message, str(id))

            return

        video = VideoMessage.decode(message)

        try:
            if (video.content['trending_date'] != None):
                id = str(self.get_instance_n(
                    video.content['trending_date']))

                self.middleware.send_video_message(message, id)
        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')

    def get_instance_n(self, key):
        return hash(key) % self.nr_instances
