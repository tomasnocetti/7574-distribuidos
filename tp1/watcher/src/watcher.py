import logging
import signal
import docker

from src.heartbeats import Heartbeats
from src.middleware import WatcherMiddlware
from src.hierarchy_worker import HierarchyWorker

WATCHER_QUEUE = "watcher_queue"
WATCHER_HIERARCHY_QUEUE = "watcher_hierarchy_queue"

class Watcher(HierarchyWorker):
    def __init__(self) -> None:
        super().__init__()
        self.heartbeats = Heartbeats()
        self.docker = docker.from_env()
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        self.watcher_middleware = WatcherMiddlware(self.id)

    def start(self):
        logging.info('Starting Watcher')
        self.heartbeats.init_hearbeats()
        super().start()
        self.watcher_middleware.run()
        self.watcher_middleware.accept_heartbeats(self.handle_heartbeat)

    def handle_heartbeat(self, heartbeat):
        logging.debug('Handling hearbeat [{}]'.format(heartbeat))
        self.heartbeats.hearbeat(heartbeat)
        unavailable_services = self.heartbeats.get_unavailable_services()
        self.wake_up_services(unavailable_services)

    def wake_up_services(self, unavailable_services: list):
        if self.im_leader():
            for service in unavailable_services:
                logging.debug("Starting unavailable service [{}]".format(service))
                self.wake_up(service)

    def wake_up(self, service):
        self.docker.api.stop(service)
        self.docker.api.start(service)

    def start_up(self, service):
        self.docker.api.stop(service)
        #Como hacer para iniciar el contenedor?
    
    def exit_gracefully(self, *args):
        logging.info('Exiting gracefully')
        super().stop()
        self.watcher_middleware.stop()