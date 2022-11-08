import logging
from common.middleware import Middleware
from multiprocessing import Process
import time

WATCHER_EXCHANGE = 'watcher_exchange'
HEARTBEAT_FRECUENCY = 1 #In seconds

logging.getLogger("pika").propagate = False

class HeartbeatMiddleware(Middleware):
    def __init__(self, heartbeat_id) -> None:
        super().__init__()
        self.reporting = False
        self.channel.exchange_declare(exchange=WATCHER_EXCHANGE, exchange_type='fanout')
        self.channel.basic_qos(prefetch_count=1)
        self.reporting_process: Process = None
        self.heartbeat_id = heartbeat_id
        
    def run(self):
        logging.info("HeartbeatMiddleware started")
        self.reporting = True
        self.reporting_process = Process(target=self.report)
        self.reporting_process.start()

    def report(self):
        while self.reporting:
            logging.info("Sending heartbeat")
            super().send_to_exchange(WATCHER_EXCHANGE, '', self.heartbeat_id)
            time.sleep(HEARTBEAT_FRECUENCY)

    def stop(self):
        self.reporting = False
        self.reporting_process.join()