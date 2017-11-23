from . import BaseCollector, entry
import os


class Collector(BaseCollector):
    def postinit(self):
        if not hasattr(os, 'getloadavg'):
            raise NotImplementedError

    def run(self):
        out = {}
        loadavg = os.getloadavg()
        out['node_load1'] = entry(
            [({}, loadavg[0])],
            'gauge',
            '1m load average.',
        )
        out['node_load5'] = entry(
            [({}, loadavg[1])],
            'gauge',
            '5m load average.',
        )
        out['node_load15'] = entry(
            [({}, loadavg[2])],
            'gauge',
            '15m load average.',
        )
        self.output = out
