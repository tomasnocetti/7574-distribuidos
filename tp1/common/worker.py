import logging
import signal

from .middleware import Middleware


class Worker():
    def __init__(self, middleware) -> None:
        self.running = True
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)

        self.middleware: Middleware = middleware

    def start(self):
        try:
            self.run()
        except OSError:
            pass

    def exit_gracefully(self, *args):
        self.running = False
        self.middleware.close_connection()
        logging.info('Exiting gracefully')
