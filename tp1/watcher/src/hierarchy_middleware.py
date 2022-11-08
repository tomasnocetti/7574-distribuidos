from ctypes import c_bool
import logging
import time
from common.middleware import Middleware
from multiprocessing import Process, Value

from src.election import Election, LeaderElection, Leader, LeaderSelected
from src.election_state import NotParticipating, Participating

MASTER_TIMEOUT = 5
HEARBEAT_FRECUENCY = 1
FIRST_INSTANCE = 0

class HierarchyMiddlware(Middleware):
    def __init__(self, neighborhood, hierarchy_id, hierarchy_instances) -> None:
        super().__init__()
        self.leader = Value('i', -1)
        self.running = Value(c_bool, False)
        self.election_state = NotParticipating()
        self.hyerarchy_id = int(hierarchy_id)
        self.neighborhood = neighborhood
        self.hyerarchy_instances = int(hierarchy_instances)
        self.neighbour_id = self._get_neighbour()
        self.leader_process: Process = None
        self.listening_process: Process = None
        self.queue = self.neighborhood + "_" + str(self.hyerarchy_id)
        self.neighbour_queue = self.neighborhood + "_" + str(self.neighbour_id)
        for slave_id in range(self.hyerarchy_instances):
            queue = self.neighborhood + "_" + str(slave_id)
            self.channel.queue_declare(queue)
        self.channel.basic_qos(prefetch_count=1)

    def _get_neighbour(self) -> int:
        if self.hyerarchy_id == (self.hyerarchy_instances - 1):
            return FIRST_INSTANCE
        return (self.hyerarchy_id + 1)

    def run(self):
        logging.info("HierarchyMiddlware started")
        self.running.value = True
        self.leader_process = Process(target=self.send_heartbeats)
        self.listening_process = Process(target=self.accept_heartbeats)
        self.leader_process.start()
        self.listening_process.start()

    def send_heartbeats(self):
        while self.running.value:
            logging.debug("Im leader? [{}]".format(self.im_leader()))
            if self.im_leader():
                logging.info("Sending heartbeat to all slaves")
                for slave_id in range(self.hyerarchy_instances):
                    if (slave_id) != self.hyerarchy_id:
                        leader_message = Leader(self.hyerarchy_id).to_string()
                        super().send_message(self.neighborhood + "_" + str(slave_id), leader_message)
            time.sleep(HEARBEAT_FRECUENCY)
            
    def im_leader(self) -> bool:
        return self.hyerarchy_id == self.leader.value

    def accept_heartbeats(self):
        while self.running.value:
            if not self.im_leader():
                # Get ten messages and break out
                for method_frame, properties, body in self.channel.consume(queue=self.queue, inactivity_timeout=MASTER_TIMEOUT):

                    if self.im_leader() or not self.running.value:
                        break

                    heartbeat = None

                    if method_frame is None and properties is None and body is None:
                        logging.info("Timeout for receive Master heartbeat")
                        self.start_election()

                    else:
                        # Display the message parts
                        logging.debug("Method Frame [{}]".format(method_frame))
                        logging.debug("Properties [{}]".format(properties))
                        logging.info("Message [{}]".format(body))
                        heartbeat = body.decode()
                        # Acknowledge the message
                        self.channel.basic_ack(method_frame.delivery_tag)
                        self.handle_heartbeat(heartbeat)
                    
    def handle_heartbeat(self, heartbeat: str):
        logging.info('Handling hearbeat [{}]'.format(heartbeat))
        election = Election.of(heartbeat)
        if Leader.is_election(election):
            logging.info("Leader is alive")
            return
        if LeaderElection.is_election(election):
            logging.info("Leader election in progress")
            self.leader.value = -1
            if NotParticipating.is_state(self.election_state):
                self.election_state = Participating()
                if self.hyerarchy_id > election.id:
                    election.id = self.hyerarchy_id
                super().send_message(self.neighbour_queue, election.to_string())
            else:
                if election.id < self.hyerarchy_id:
                    pass #Do Nothing
                if election.id > self.hyerarchy_id:
                    super().send_message(self.neighbour_queue, heartbeat)
                if election.id == self.hyerarchy_id:
                    logging.debug("Im the New Leader!")
                    self.election_state = NotParticipating()
                    leader_selected = LeaderSelected(self.hyerarchy_id)
                    super().send_message(self.neighbour_queue, leader_selected.to_string())
        if LeaderSelected.is_election(election):
            logging.info("New Leader was selected [{}]".format(election.id))
            self.leader.value = election.id
            self.election_state = NotParticipating()
            if election.id != self.hyerarchy_id:
                super().send_message(self.neighbour_queue, heartbeat)
            logging.debug("New leader saved [{}]".format(self.leader))

    def start_election(self):
        logging.info("Starting master election")
        self.leader.value = -1
        election = LeaderElection(self.hyerarchy_id)
        super().send_message(self.neighbour_queue, election.to_string())

    def stop(self):
        self.running.value = False
        self.leader_process.join()
        self.listening_process.join()
        # Cancel the consumer and return any pending messages
        requeued_messages = self.channel.cancel()
        logging.info('Requeued %i messages Hierarchy Middleware' % requeued_messages)
        # Close the channel and the connection
        self.channel.close()
        self.connection.close()