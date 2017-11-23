from . import BaseCollector, entry
import re


class Collector(BaseCollector):
    def run(self):
        out = {}
        lines = []
        with open('/proc/meminfo') as f:
            for l in f:
                lines.append(re.split('\s+', l.strip()))
        for l in lines:
            if len(l) == 2:
                v = int(l[1])
            elif len(l) == 3:
                if l[2] == 'kB':
                    v = int(l[1]) * 1024
                else:
                    continue
            else:
                continue
            k = l[0].replace(':', '').replace('(', '_').replace(')', '')
            out['node_memory_%s' % k] = entry(
                [({}, v)],
                'gauge',
                'Memory information field %s.' % k,
            )
        self.output = out
