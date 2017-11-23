from . import BaseCollector, entry
import time


class Collector(BaseCollector):
    def run(self):
        out = {}
        out['node_time'] = entry(
            [({}, int(time.time()))],
            'gauge',
            'System time in seconds since epoch (1970).',
        )
        self.output = out
