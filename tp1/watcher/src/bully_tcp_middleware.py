import logging
import socket
from ctypes import c_bool
from multiprocessing import Process, Value
from src.election_message import ELECTION_LENGTH_MESSAGE, ErrorMessage, TimeoutMessage

BUFFER_SIZE = 1024
ENCODING = "utf-8"

class BullyTCPMiddleware(object):
    """BullyTCPMiddlware
    This class provides a communication layer between bully workers.
    The communication can be 
        * Master - Slave
        * Slave - Slave
    """

    def __init__(self, port, bully_id, bully_instances, work_group) -> None:
        """
        Creates a new istance of BullyTCPMiddlware
        """
        self.port = int(port)
        self.bully_id = int(bully_id)
        self.bully_instances = int(bully_instances)
        self.work_group = work_group
        self.server_socket = None
        self.server_process = None
        ####CRITIC SECTION####
        self.running = Value(c_bool, False)
        ######################
    
    def run(self, callback):
        logging.info("BullyTCPMiddlware started")
        self.running.value = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(self.bully_instances)
        self.server_process = Process(target=self._accept_connections, args=(self.server_socket, callback))
        self.server_process.start()

    def _accept_connections(self, socket: socket.socket, callback):
        logging.debug("Accept connections in port [{}]".format(self.port))
        while self.running.value:
            try:
                connection, _addr = socket.accept()
                self._handle_connection(connection, callback)
            except OSError as error:
                logging.error("Error while accept connection in server socket {}. Error: {}".format(self.server_socket, error))
                socket.close()
                break
            
    def _handle_connection(self, connection: socket.socket, callback):
        logging.debug("Handling connection [{}]".format(connection))
        expected_length_message = ELECTION_LENGTH_MESSAGE + len(str(self.bully_instances))
        message = self._recv(connection, expected_length_message)
        callback(connection, message)

    def send_to_infs(self, message: str, timeout: int, callback) -> list['bool']:
        instances = range(self.bully_id)
        return self._send_to(message, instances, timeout, callback)

    def send_to_sups(self, message: str, timeout: int, callback) -> list['bool']:
        instances = range(self.bully_id, self.bully_instances)
        return self._send_to(message, instances, timeout, callback)

    def send_to_all(self, message: str, timeout: int, callback) -> list['bool']:
        instances = range(self.bully_instances)
        return self._send_to(message, instances, timeout, callback)
    
    def _send_to(self, message: str, instances: list['int'], timeout, callback) -> list['bool']:
        sends_sucessfully = list()
        for instance_id in instances:
            if instance_id != self.bully_id:
                send_sucessfully = self.send(message, instance_id, timeout, callback)
                sends_sucessfully.append(send_sucessfully)
        return sends_sucessfully

    def send(self, message: str, instance_id: int, timeout: int, callback) -> bool:
        """Send
           Send message to a instance.
           If a `timeout` is specified, it waits to receive a response in that period of time.
           Return bool representation of send successfully.
        """
        sends_sucessfully = False
        host = self.work_group + "_" + str(instance_id)
        port = self.port
        logging.info("Sending [{}] to Host [{}] and Port [{}]".format(message, host, port))
        try:
            with socket.create_connection((host, port)) as connection:
                connection.sendall(message.encode(ENCODING))
                expected_length_message = ELECTION_LENGTH_MESSAGE + len(str(self.bully_instances))
                response = self._recv_timeout(connection, expected_length_message, timeout)
                sends_sucessfully = callback(connection, response)
        except socket.error as error:
            logging.error("Error while create connection to socket. Error: {}".format(error))
        return sends_sucessfully

    def send_to_connection(self, message: str, connection: socket.socket):
        connection.sendall(message.encode(ENCODING))

    def _recv(self, connection: socket.socket, expected_length_message: int) -> str:
        data = b''
        while len(data) < expected_length_message:
            try:
                data += connection.recv(BUFFER_SIZE)
            except socket.error as error:
                logging.error("Error while recv data from connection {}. Error: {}".format(connection, error))
                return ErrorMessage().to_string()
        return data.decode(ENCODING)

    def _recv_timeout(self, connection: socket.socket, expected_length_message: int, timeout: float) -> str:
        data = b''
        connection.settimeout(timeout)
        while len(data) < expected_length_message:
            try:
                data += connection.recv(BUFFER_SIZE)
            except socket.timeout as timeout:
                logging.error("Timeout for recv data from connection {}. Error: {}".format(connection, timeout))
                return TimeoutMessage().to_string()
            except socket.error as error:
                logging.error("Error while recv data from connection {}. Error: {}".format(connection, error))
                return ErrorMessage().to_string()
        connection.settimeout(None)
        return data.decode(ENCODING)

    def stop(self):
        self.running.value = False
        self.server_socket.close()
        self.server_process.join()
        logging.info('BullyTCPMiddlware Stopped')