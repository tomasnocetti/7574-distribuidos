import os
from .heartbeat_job import HearthbeatJob
from .worker import Worker


class HeartbeathedWorker(Worker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.heartbeat_job = HearthbeatJob()

    def start(self):
        self.heartbeat_job.start()
        super().start()

    def exit_gracefully(self, *args):
        self.heartbeat_job.stop()
        super().exit_gracefully()
