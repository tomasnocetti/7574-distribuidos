from datetime import datetime
import logging
import os

from common.constants import NO_HEARTBEAT_CODE, SERVICE_HEARTBEAT_TIMEOUT

class Heartbeats:
    def __init__(self) -> None:
        self.hearbeats = dict()

    def hearbeat(self, service_id):
        if service_id:
            self.hearbeats[service_id] = self._get_current_timestamp()

    def init_hearbeats(self):
        joiner_instances = int(os.environ['JOINER_INSTANCES'])
        dropper_instances = int(os.environ['DROPPER_INSTANCES'])
        trending_instances = int(os.environ['TRENDING_INSTANCES'])
        thumbnail_instances = int(os.environ['THUMBNAIL_INSTANCES'])
        like_filter_instances = int(os.environ['LIKE_FILTER_INSTANCES'])
        self._init_service_hearbeats("joiner", joiner_instances)
        self._init_service_hearbeats("dropper", dropper_instances)
        self._init_service_hearbeats("trending", trending_instances)
        self._init_service_hearbeats("thumbnail", thumbnail_instances)
        self._init_service_hearbeats("like_filter", like_filter_instances)

    def _init_service_hearbeats(self, service_name, service_instances):
        for i in range(service_instances):
            service_id = service_name + "_" + str(i)
            self.hearbeat(service_id)

    def get_unavailable_services(self) -> list:
        unavailable_services = list()
        for service_id in self.hearbeats:
            current_timestamp = self._get_current_timestamp()
            service_last_timestamp = self.hearbeats.get(service_id)
            timeout_timestamp = SERVICE_HEARTBEAT_TIMEOUT + service_last_timestamp
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