
import os
from src.hierarchy_middleware import HierarchyMiddlware

WATCHER_GROUP = "watcher"

class HierarchyWorker:
    def __init__(self) -> None:
        self.id = os.environ['SERVICE_ID']
        self.hyerarchy_id = os.environ['INSTANCE_ID']
        self.hyerarchy_instances = os.environ['WATCHERS_INSTANCES']
        self.hierarchy_middleware = HierarchyMiddlware(WATCHER_GROUP, self.hyerarchy_id, self.hyerarchy_instances)

    def im_leader(self) -> bool:
        return self.hierarchy_middleware.im_leader()

    def start(self):
        self.hierarchy_middleware.run()

    def stop(self):
        self.hierarchy_middleware.stop()
