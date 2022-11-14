
import logging
import os

from src.bully_tcp_middleware import BullyTCPMiddlware

class BullyTCPWorker:
    """BullyTCPWorker
    This class represents worker with specific Bully Relationship.
    The Master is worker who has responsability to perform a certain activity.
    The Slaves are replicated workers to ensure the availability of the task to be executed.
    Implements Bully algorithm leader election.
    """
    def __init__(self) -> None:
        self.id = os.environ['SERVICE_ID']
        self.port = os.environ['SERVICE_PORT']
        self.instance_id = os.environ['INSTANCE_ID']
        self.bully_instances = os.environ['WATCHERS_INSTANCES']
        self.bully_middleware = BullyTCPMiddlware(self.port, self.instance_id, self.bully_instances)

    def start(self):
        logging.info("BullyTCPWorker started")
        self.bully_middleware.run()

    def im_leader(self) -> bool:
        return self.bully_middleware.im_leader()

    def stop(self):
        self.bully_middleware.stop()
        logging.info('BullyTCPWorker Stopped')
