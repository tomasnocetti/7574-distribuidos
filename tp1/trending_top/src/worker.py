import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import EndResult3, Result3


class TrendingTop(HeartbeathedWorker):
    def __init__(self, middleware, trending_instances) -> None:
        super().__init__(middleware)
        self.results_counter = 0
        self.top_date = ''
        self.top_views = 0
        self.trending_instances = trending_instances

    def run(self):
        self.middleware.recv_result_message(self.recv_results)

    def recv_results(self, message):

        message = Result3.decode(message)
        values = message.content.split(',')
        date = values[0]
        views = int(values[1])

        logging.info(f'{date}, {views}')
        if (views > self.top_views):
            self.top_date = date
            self.top_views = views

        self.results_counter += 1

        if (self.results_counter == self.trending_instances):
            message = Result3(message.client_id, "FINAL_RESULT", self.top_date)
            self.middleware.send_result_message(message.pack())

            end_message = EndResult3(message.client_id, "FINAL_RESULT")
            self.middleware.send_result_message(end_message.pack())
            self.results_counter = 0
            self.top_date = ''
            self.top_views = 0
