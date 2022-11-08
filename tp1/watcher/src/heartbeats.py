from datetime import datetime
import logging

SERVICE_TIMEOUT_SECONDS = 5

class Heartbeats:
    def __init__(self) -> None:
        self.hearbeats = dict()

    def hearbeat(self, service_id):
        if service_id:
            self.hearbeats[service_id] = self._get_current_timestamp()

    def get_unavailable_services(self) -> list:
        unavailable_services = list()
        for service_id in self.hearbeats:
            current_timestamp = self._get_current_timestamp()
            service_last_timestamp = self.hearbeats.get(service_id)
            timeout_timestamp = SERVICE_TIMEOUT_SECONDS + service_last_timestamp
            logging.debug("Current Timestamp [{}]. Service Timeout Timestamp [{}]".format(current_timestamp, timeout_timestamp))
            if current_timestamp > timeout_timestamp:
                logging.info("Service [{}] is unavailable".format(service_id))
                unavailable_services.append(service_id)
        for unavailable_service in unavailable_services:
            self.hearbeats.pop(unavailable_service)
        return unavailable_services

    def _get_current_timestamp(self) -> float:
        # Getting the current date and time
        dt = datetime.now()
        # getting the timestamp
        timestamp = datetime.timestamp(dt)
        return timestamp