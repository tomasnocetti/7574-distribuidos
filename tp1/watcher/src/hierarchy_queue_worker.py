
import os
from src.hierarchy_queue_middleware import HierarchyQueueMiddlware

WATCHER_GROUP = "watcher"

class HierarchyQueueWorker:
    """HierarchyQueueWorker
    This class represents worker with specific Hierarchy.
    The Master is worker who has responsability to perform a certain activity.
    The Slaves are replicated workers to ensure the availability of the task to be executed.
    """
    def __init__(self) -> None:
        self.id = os.environ['SERVICE_ID']
        self.hyerarchy_id = os.environ['INSTANCE_ID']
        self.hyerarchy_instances = os.environ['WATCHERS_INSTANCES']
        self.hierarchy_middleware = HierarchyQueueMiddlware(WATCHER_GROUP, self.hyerarchy_id, self.hyerarchy_instances)

    def im_leader(self) -> bool:
        return self.hierarchy_middleware.im_leader()

    def start(self):
        self.hierarchy_middleware.run()

    def stop(self):
        self.hierarchy_middleware.stop()
