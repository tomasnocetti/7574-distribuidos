from ctypes import c_bool, c_int
import logging
import socket
import time
from multiprocessing import Process, Value
from src.election_message import ELECTION_LENGTH_MESSAGE, AliveAnswerMessage, AliveMessage, ElectionMessage, ErrorMessage, LeaderElectionMessage, ElectionAnswerMessage, CoordinatorMessage, TimeoutMessage

BUFFER_SIZE = 1024
ENCODING = "utf-8"

NO_LEADER = -1
CHECK_RETRIES = 3

LEADER_TIMEOUT = 10 #In seconds
SLAVES_TIMEOUT = 10 #In seconds
ELECTION_TIMEOUT = 10 #In seconds
CHECK_FRECUENCY = 5 #In seconds

class BullyTCPMiddlware:
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
        ####CRITIC SECTION####
        self.running = Value(c_bool, False)
        self.leader = Value(c_int, NO_LEADER)
        ######################
        self.port = int(port)
        self.bully_id = int(bully_id)
        self.bully_instances = int(bully_instances)
        self.work_group = work_group
        self.start_process: Process = None
        self.check_process: Process = None
        self.listening_process: Process = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(self.bully_instances)

    def run(self):
        logging.info("BullyTCPMiddlware started")
        self.running.value = True
        self.listening_process = Process(target=self._accept_connections)
        self.listening_process.start()
        self.start_process = Process(target=self.start)
        self.start_process.start()
        self.check_process = Process(target=self._check_alive)
        self.check_process.start()

    def start(self):
        """Start.
           If process started has higher ID, takes the leadership and tells to other process.
           Otherwise it starts leader election.
        """
        if self.bully_id == (self.bully_instances -1):
            self._setme_as_leader()
        else:
            self._start_election()

    def _accept_connections(self):
        logging.debug("Accept connections in port [{}]".format(self.port))
        while self.running.value:
            try:
                connection, _addr = self.server_socket.accept()
                self._handle_connection(connection)
            except OSError as error:
                logging.error("Error while accept connection in server socket {}. Error: {}".format(self.server_socket, error))
                self.server_socket.close()
            
    def _handle_connection(self, connection: socket.socket):
        logging.debug("Handling connection [{}]".format(connection))
        expected_length_message = ELECTION_LENGTH_MESSAGE + len(str(self.bully_instances))
        message = self._recv(connection, expected_length_message)
        self._handle_message(connection, message)

    def _check_alive(self):
        while self.running.value:
            if (self.leader.value != NO_LEADER) and self.im_leader():
                self._check_slaves_alive()
            elif (self.leader.value != NO_LEADER) and not self.im_leader():
                self._check_leader_alive()
            time.sleep(CHECK_FRECUENCY)

    def _check_slaves_alive(self):
        for instance_id in range(self.bully_instances):
            if instance_id != self.bully_id:
                checking_tries = 0
                message = AliveMessage(self.bully_id).to_string()
                while checking_tries < CHECK_RETRIES:
                    logging.info("Checking slave alives")
                    slave_response = self._send(message, instance_id, SLAVES_TIMEOUT)
                    if not slave_response:
                        checking_tries+=1
                        time.sleep(CHECK_FRECUENCY)
                    else:
                        break 
                if checking_tries == CHECK_RETRIES:
                    logging.info("Slave [{}] is not responding".format(instance_id))

    def _check_leader_alive(self):
        checking_tries = 0
        message = AliveMessage(self.bully_id).to_string()
        while checking_tries < CHECK_RETRIES:
            logging.info("Checking leader alives")
            leader_response = self._send(message, self.leader.value, LEADER_TIMEOUT)
            if not leader_response:
                checking_tries+=1
                time.sleep(CHECK_FRECUENCY)
            else:
                break 
        if checking_tries == CHECK_RETRIES:
            logging.info("Leader [{}] is not responding".format(self.leader.value))
            self._start_election() 

    def _send_to_infs(self, message: str, timeout: int) -> list['bool']:
        instances = range(self.bully_id)
        return self._send_to(message, instances, timeout)

    def _send_to_sups(self, message: str, timeout: int) -> list['bool']:
        instances = range(self.bully_id, self.bully_instances)
        return self._send_to(message, instances, timeout)

    def _send_to_all(self, message: str, timeout: int) -> list['bool']:
        instances = range(self.bully_instances)
        return self._send_to(message, instances, timeout)
    
    def _send_to(self, message: str, instances: list['int'], timeout) -> list['bool']:
        sends_sucessfully = list()
        for instance_id in instances:
            if instance_id != self.bully_id:
                send_sucessfully = self._send(message, instance_id, timeout)
                sends_sucessfully.append(send_sucessfully)
        return sends_sucessfully

    def _send(self, message: str, instance_id: int, timeout: int) -> bool:
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
                sends_sucessfully = self._handle_message(connection, response)
        except socket.error as error:
            logging.error("Error while create connection to socket. Error: {}".format(error))
        return sends_sucessfully

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

    def _handle_message(self, connection: socket.socket, message: str) -> bool:
        """Handle Message
           This method handle message from connection and returns boolean representation of handle.
           If handle successfully returns True otherwise returns False.
        """
        logging.info('Handling Message [{}]'.format(message))
        election = ElectionMessage.of(message)
        if TimeoutMessage.is_election(election):
            logging.info("Timeout message!")
            return False
        elif ErrorMessage.is_election(election):
            logging.info("Error message!")
            return False
        elif AliveMessage.is_election(election):
            alive_answer_message = AliveAnswerMessage(self.bully_id).to_string()
            logging.info("Responding alive message")
            connection.sendall(alive_answer_message.encode(ENCODING))
        elif LeaderElectionMessage.is_election(election):
            logging.info("Leader election in progress")
            self.leader.value = NO_LEADER
            election_answer_message = ElectionAnswerMessage(self.bully_id)
            connection.sendall(election_answer_message.to_string().encode(ENCODING))
            self._start_election()
        elif AliveAnswerMessage.is_election(election):
            if self.im_leader():
                logging.info("Slave is alive")
            else:
                logging.info("Leader is alive")
        elif ElectionAnswerMessage.is_election(election):
            logging.info("Election answer message receive")
        elif CoordinatorMessage.is_election(election):
            self.leader.value = election.id
            if self.im_leader():
                logging.info("Coordination message answer message receive")
            else:
                logging.info("New Leader was selected [{}]".format(election.id))
                connection.sendall(message.encode(ENCODING))
        return True

    def _start_election(self):
        logging.info("Starting leader election")
        self.leader.value = NO_LEADER
        election = LeaderElectionMessage(self.bully_id)
        election_responses = self._send_to_sups(election.to_string(), ELECTION_TIMEOUT)
        if not any(election_responses):
            self._setme_as_leader()

    def _setme_as_leader(self):
        logging.info("Setting me as leader and tell others")
        self.leader.value = self.bully_id
        election = CoordinatorMessage(self.bully_id)
        self._send_to_all(election.to_string(), ELECTION_TIMEOUT)

    def im_leader(self) -> bool:
        return (self.bully_id == self.leader.value)

    def stop(self):
        self.running.value = False
        self.check_process.join()
        self.start_process.join()
        self.listening_process.join()
        self.server_socket.close()
        logging.info('BullyTCPMiddlware Stopped')