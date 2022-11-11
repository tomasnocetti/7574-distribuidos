import os
from .heartbeat_middleware import HeartbeatMiddleware
from .worker import Worker

class HeartbeathedWorker(Worker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.id = os.environ['SERVICE_ID']
        self.heartbeat_middleware = HeartbeatMiddleware(self.id)

    def start(self):
        try:
            self.heartbeat_middleware.run()
        except OSError:
            pass
        super().start()

    def exit_gracefully(self, *args):
        self.heartbeat_middleware.stop()
        super().exit_gracefully()
