from . import BaseCollector, entry
import os


class Collector(BaseCollector):
    def __init__(self):
        if not os.path.exists('/proc/sys/kernel/random/entropy_avail'):
            raise NotImplementedError

    def run(self):
        out = {}
        with open('/proc/sys/kernel/random/entropy_avail') as f:
            out['node_entropy_available_bits'] = entry(
                [({}, int(f.read().rstrip()))],
                'gauge',
                'Bits of available entropy.',
            )
        self.output = out
