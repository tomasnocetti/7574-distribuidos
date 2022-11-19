import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import MessageEnd, Result3, VideoMessage
from datetime import datetime


class TrendingInstance(HeartbeathedWorker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.dates = {}

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            end_message = MessageEnd.decode(message)
            logging.info(
                f'Finish Recv Videos: {len(self.dates)}')

            self.process_and_send_results(end_message.client_id)
            return

        video = VideoMessage.decode(message)

        try:

            if (video.content['trending_date'] != None and video.content['view_count'] != None):
                date = datetime.strptime(
                    video.content['trending_date'], '%Y-%m-%dT%H:%M:%SZ')

                views = int(video.content['view_count'])
                self.group_date(date, views)

        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')
        except ValueError:
            logging.error(
                f'Incorrect formatted value {video.content}')

    def process_and_send_results(self, client_id):

        max_date = ''
        max_number = 0

        for date in self.dates:
            if(self.dates[date] > max_number):
                max_number = self.dates[date]
                max_date = date

        result = Result3(client_id, "TODO:INSTANCE_ID", f"{max_date},{max_number}")
        self.middleware.send_result_message(result.pack())

        self.dates = {}
        return

    def group_date(self, date, views):

        datem = date.strftime("%Y-%m-%d")
        self.dates.setdefault(datem, 0)
        self.dates[datem] += views
        # logging.info(self.dates[datem])
        return
