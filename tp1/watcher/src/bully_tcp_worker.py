
import os
import time
import docker
import logging
from ctypes import c_bool, c_int
from multiprocessing import Process, Value

from src.bully_tcp_middleware import BullyTCPMiddleware
from src.election_message import AliveAnswerMessage, AliveMessage, CoordinatorMessage, ElectionAnswerMessage, ElectionMessage, ErrorMessage, LeaderElectionMessage, TimeoutMessage

NO_LEADER = -1
CHECK_RETRIES = 3

LEADER_TIMEOUT = 10 #In seconds
SLAVES_TIMEOUT = 10 #In seconds
ELECTION_TIMEOUT = 10 #In seconds
CHECK_FRECUENCY = 5 #In seconds

class BullyTCPWorker:
    """BullyTCPWorker\n
    This class represents worker with specific Bully Relationship.\n
    The Master is worker who has responsability to perform a certain activity.\n
    The Slaves are replicated workers to ensure the availability of the task to be executed.\n
    Implements Bully algorithm leader election.
    """
    def __init__(self, work_group) -> None:
        self.id = os.environ['SERVICE_ID']
        self.port = int(os.environ['SERVICE_PORT'])
        self.bully_id = int(os.environ['INSTANCE_ID'])
        self.bully_instances = int(os.environ['WATCHERS_INSTANCES'])
        self.work_group = work_group
        self.bully_middleware = BullyTCPMiddleware(self.port, self.bully_id, self.bully_instances, self.work_group)
        self.middleware_process: Process = None
        self.start_bully_process: Process = None
        self.check_process: Process = None
        self.docker = docker.from_env()
        ####CRITIC SECTION####
        self.running = Value(c_bool, False)
        self.leader = Value(c_int, NO_LEADER)
        ######################

    def start(self):
        """Start\n
            Starts Bully processes
            - Bully Middleware process (Backgroud process)
            - Bully Init process (Backgroud process)
            - Bully Check process (Backgroud process)\n
            Each process will have a copy of the middleware. 
        """
        logging.info("BullyTCPWorker started")
        self.running.value = True
        self.middleware_process = Process(target=self._start_middleware)
        self.middleware_process.start()
        self.start_bully_process = Process(target=self._start_bully)
        self.start_bully_process.start()
        self.check_process = Process(target=self._check_alive)
        self.check_process.start()
    
    def _start_middleware(self):
        """Start Middleware\n
            Starts Bully Middleware process and waits for Bully worker stop.\n
            This process has `bully_middleware` copy responsable to accept conections and handle messages.
        """
        self.bully_middleware.run(self._handle_message)
        while self.running.value:
            continue
        self.bully_middleware.stop()

    def _start_bully(self):
        """Start Bully\n
            This process has `bully_middleware` copy responsable to start bully algorithm.\n
            If process started has higher ID, takes the leadership and tells to other process. Otherwise it starts leader election.\n
            This process may run only once in bully worker startup.
        """
        if self.bully_id == (self.bully_instances -1):
            self._setme_as_leader()
        else:
            self._start_election()

    def _check_alive(self):
        """Check Alive\n
            This process has `bully middleware` copy responsible to check alives entities until bully worker is stopped.
            This process may run only once in bully worker startup.
            - Leader check
            - Slave check
        """
        while self.running.value:
            if (self.leader.value != NO_LEADER) and self.im_leader():
                self._check_slaves_alive()
            elif (self.leader.value != NO_LEADER) and not self.im_leader():
                self._check_leader_alive()
            time.sleep(CHECK_FRECUENCY)

    def _check_slaves_alive(self):
        logging.info("Checking slaves alives")
        for instance_id in range(self.bully_instances):
            if instance_id != self.bully_id:
                checking_tries = 0
                message = AliveMessage(self.bully_id).to_string()
                while checking_tries < CHECK_RETRIES:
                    slave_response = self.bully_middleware.send(message, instance_id, SLAVES_TIMEOUT, self._handle_message)
                    if not slave_response:
                        checking_tries+=1
                        time.sleep(CHECK_FRECUENCY)
                    else:
                        break 
                if checking_tries == CHECK_RETRIES:
                    logging.info("Slave [{}] is not responding".format(instance_id))
                    self.wake_up_slave(instance_id)

    def _check_leader_alive(self):
        """Check Leader Alive\n
            Here `bully middleware` copy is responsible to check alives start new election if leader is not responding.
        """
        logging.info("Checking leader alives")
        checking_tries = 0
        message = AliveMessage(self.bully_id).to_string()
        while checking_tries < CHECK_RETRIES:
            leader_response = self.bully_middleware.send(message, self.leader.value, LEADER_TIMEOUT, self._handle_message)
            if not leader_response:
                checking_tries+=1
                time.sleep(CHECK_FRECUENCY)
            else:
                break 
        if checking_tries == CHECK_RETRIES:
            logging.info("Leader [{}] is not responding".format(self.leader.value))
            self._start_election()

    def wake_up_slave(self, instance_id):
        logging.info("Waking up instance with id [{}]".format(instance_id))
        service = self.work_group + "_" + str(instance_id)
        self.docker.api.stop(service)
        self.docker.api.start(service)

    def _start_election(self):
        """Start Election\n
           This method starts new leader election acording to Bully Algorithm.\n
           - Sends a Leader Election Message and waits for Answer Election Message
           - If no answer received, it proclaims himself as a leader
        """
        logging.info("Starting leader election")
        self.leader.value = NO_LEADER
        election = LeaderElectionMessage(self.bully_id)
        election_responses = self.bully_middleware.send_to_sups(election.to_string(), ELECTION_TIMEOUT, self._handle_message)
        if not any(election_responses):
            self._setme_as_leader()

    def _setme_as_leader(self):
        """Set me As Leader\n
           Proclaims himself as a leader.
        """
        logging.info("Setting me as leader and tell others")
        self.leader.value = self.bully_id
        election = CoordinatorMessage(self.bully_id)
        self.bully_middleware.send_to_all(election.to_string(), ELECTION_TIMEOUT, self._handle_message)

    def _handle_message(self, connection, message: str) -> bool:
        """Handle Message\n
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
            self.bully_middleware.send_to_connection(alive_answer_message, connection)
        elif LeaderElectionMessage.is_election(election):
            logging.info("Leader election in progress")
            self.leader.value = NO_LEADER
            election_answer_message = ElectionAnswerMessage(self.bully_id).to_string()
            self.bully_middleware.send_to_connection(election_answer_message, connection)
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
                self.bully_middleware.send_to_connection(message, connection)
        return True

    def im_leader(self) -> bool:
        return (self.bully_id == self.leader.value)

    def stop(self):
        """Stop\n
            Stops bully worker and waits for all worker process to finish.
        """
        self.running.value = False
        self.start_bully_process.join()
        self.check_process.join()
        self.middleware_process.join()
        logging.info('BullyTCPWorker Stopped')
