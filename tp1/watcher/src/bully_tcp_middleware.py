from ctypes import c_bool
import logging
import socket
import time
from multiprocessing import Process, Value
from src.election_message import BASE_LENGTH_MESSAGE, AliveMessage, ElectionMessage, LeaderElectionMessage, AnswerMessage, CoordinatorMessage

WATCHER_GROUP = "watcher"
BUFFER_SIZE = 1024
ENCODING = "utf-8"

LEADER_TIMEOUT = 5 #In seconds
CHECK_FRECUENCY = 1 #In seconds
FIRST_INSTANCE = 0
NO_LEADER = -1

class BullyTCPMiddlware:
    """BullyTCPMiddlware
    This class provides a communication layer between bully workers.
    The communication can be 
        * Master - Slave
        * Slave - Slave
    """

    def __init__(self, port, bully_id, bully_instances) -> None:
        """
        Creates a new istance of BullyTCPMiddlware
        """
        self.port = int(port)
        self.bully_id = int(bully_id)
        self.running = Value(c_bool, False)
        self.bully_instances = int(bully_instances)
        self.init_leader()
        self.check_process: Process = None
        self.listening_process: Process = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(self.bully_instances)

    def init_leader(self):
        if self.bully_id == (self.bully_instances - 1):
            self.leader = Value('i', self.bully_id)
        else:
            self.leader = Value('i', NO_LEADER)

    def run(self):
        logging.info("BullyTCPMiddlware started")
        self.running.value = True
        #self.listening_process = Process(target=self._accept_connections)
        #self.listening_process.start()
        #self._send_first_leader()
        #self.check_process = Process(target=self._check_leader_alive)
        #self.check_process.start()

    def _send_first_leader(self):
        if self.im_leader():
            logging.info("Sending first coordinator message")
            election = CoordinatorMessage(self.bully_id)
            self._send_to_all(election.to_string())

    def _accept_connections(self):
        logging.info("Accept connections in port [{}]".format(self.port))
        while self.running.value:
            try:
                connection, _addr = self.server_socket.accept()
                self._handle_connection(connection)
            except OSError as error:
                logging.error("Error while accept connection in server socket {}. Error: {}".format(self.server_socket, error))
                self.server_socket.close()
            
    def _handle_connection(self, connection: socket.socket):
        logging.info("Handling connection [{}]".format(connection))
        expected_length_message = BASE_LENGTH_MESSAGE + len(str(self.bully_instances))
        message = self._recv(connection, expected_length_message)
        self._handle_message(connection, message)

    def _check_leader_alive(self):
        while self.running.value:
            if not self.im_leader():
                logging.info("Checking leader alives")
                with self.leader.get_lock():
                    host = WATCHER_GROUP + "_" + str(self.leader.value)
                    port = self.port
                    with socket.create_connection((host, port)) as connection:
                        message = AliveMessage(self.bully_id)
                        connection.sendall(message.to_string().encode(ENCODING))
                        expected_length_message = BASE_LENGTH_MESSAGE + len(str(self.bully_instances))
                        response = self._recv(connection, expected_length_message)
                        self._handle_message(connection, response)
            time.sleep(CHECK_FRECUENCY)

    def _send_to_sups(self, message: str):
        for instance_id in range(self.bully_id, self.bully_instances):
            if (instance_id) != self.bully_id:
                host = WATCHER_GROUP + "_" + str(instance_id)
                port = self.port
                with socket.create_connection((host, port)) as connection:
                    connection.sendall(message.encode(ENCODING))
                    expected_length_message = BASE_LENGTH_MESSAGE + len(str(self.bully_instances))
                    response = self._recv(connection, expected_length_message)
                    self._handle_message(connection, response)

    def _send_to_all(self, message: str):
        for instance_id in range(self.bully_instances):
            if (instance_id) != self.bully_id:
                host = WATCHER_GROUP + "_" + str(instance_id)
                port = self.port
                with socket.create_connection((host, port)) as connection:
                    connection.sendall(message.encode(ENCODING))
                    expected_length_message = BASE_LENGTH_MESSAGE + len(str(self.bully_instances))
                    response = self._recv(connection, expected_length_message)
                    self._handle_message(connection, response)

    def _recv(self, connection: socket.socket, expected_length_message: int):
        data = b''
        while len(data) < expected_length_message:
            try:
                data += connection.recv(BUFFER_SIZE)
            except socket.error as error:
                logging.error("Error while recv data from connection {}. Error: {}".format(connection, error))
        return data.decode(ENCODING)

    def _handle_message(self, connection: socket.socket, message: str):
        logging.info('Handling Message [{}]'.format(message))
        election = ElectionMessage.of(message)
        if AliveMessage.is_election(election):
            if self.im_leader():
                logging.info("Responding alive message")
                connection.sendall(message.encode(ENCODING))
            else:
                logging.info("Leader is alive")
        if LeaderElectionMessage.is_election(election):
            logging.info("Leader election in progress")
            with self.leader.get_lock():
                self.leader.value = NO_LEADER
            answer_message = AnswerMessage(self.bully_id)
            connection.sendall(answer_message.to_string().encode(ENCODING))
            self._start_election()
        if AnswerMessage.is_election(election):
            logging.info("Leader election answer message receive")
        if CoordinatorMessage.is_election(election):
            if self.im_leader():
                logging.info("Coordination message answer message receive")
            else:
                logging.info("New Leader was selected [{}]".format(election.id))
                with self.leader.get_lock():
                    self.leader.value = election.id
                connection.sendall(message.encode(ENCODING))

    def _start_election(self):
        logging.info("Starting master election")
        with self.leader.get_lock():
            self.leader.value = NO_LEADER
        election = LeaderElectionMessage(self.bully_id)
        self._send_to_sups(election.to_string())

    def im_leader(self) -> bool:
        im_the_leader = False
        with self.leader.get_lock():
            im_the_leader = (self.bully_id == self.leader.value)
        return im_the_leader

    def stop(self):
        self.running.value = False
        #self.check_process.join()
        #self.listening_process.join()
        self.server_socket.close()