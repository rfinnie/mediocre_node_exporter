from . import BaseCollector, entry
import os


class Collector(BaseCollector):
    def postinit(self):
        if not os.path.exists(os.path.join(self.config.procfs, 'vmstat')):
            raise NotImplementedError

    def run(self):
        out = {}
        lines = []
        with open(os.path.join(self.config.procfs, 'vmstat')) as f:
            for l in f:
                lines.append(l.rstrip().split(' '))
        for l in lines:
            k = l[0]
            v = int(l[1])
            out['node_vmstat_%s' % k] = entry(
                [({}, v)],
                'untyped',
                '/proc/vmstat information field %s.' % k,
            )
        self.output = out
