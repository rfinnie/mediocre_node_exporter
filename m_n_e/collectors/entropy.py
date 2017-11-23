from . import BaseCollector, entry
import os


class Collector(BaseCollector):
    def run(self):
        out = {}
        if os.path.exists('/proc/sys/kernel/random/entropy_avail'):
            with open('/proc/sys/kernel/random/entropy_avail') as f:
                out['node_entropy_available_bits'] = entry(
                    [({}, int(f.read().rstrip()))],
                    'gauge',
                    'Bits of available entropy.',
                )
        self.output = out
