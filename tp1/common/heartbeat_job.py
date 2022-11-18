import logging
from .heartbeat_middleware import HeartbeatMiddleware
from multiprocessing import Process
import time
import os
import signal

HEARTBEAT_FRECUENCY = 1  # In seconds


class HearthbeatJob():
    def __init__(self) -> None:
        self.process = Process(target=self.run)
        self.running = True

    def start(self):
        self.process.start()

    def run(self):
        id = os.environ['SERVICE_ID']
        self.middleware = HeartbeatMiddleware(id)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)

        try:
            while self.running:
                self.middleware.send_heartbeat()
                time.sleep(HEARTBEAT_FRECUENCY)

        except OSError:
            pass

    def exit_gracefully(self, *args):
        logging.info("Exiting Heartbeat Job")
        self.running = False

    def stop(self):
        self.process.terminate()
