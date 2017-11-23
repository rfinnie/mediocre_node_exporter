from . import BaseCollector, entry


class Collector(BaseCollector):
    def run(self):
        out = {}
        lines = []
        with open('/proc/vmstat') as f:
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
