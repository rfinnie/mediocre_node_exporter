from . import BaseCollector, entry
import re
import os


class Collector(BaseCollector):
    def postinit(self):
        if not os.path.exists(os.path.join(self.config.procfs, 'meminfo')):
            raise NotImplementedError
        self.re_whitespace = re.compile('\s+')

    def run(self):
        out = {}
        lines = []
        with open(os.path.join(self.config.procfs, 'meminfo')) as f:
            for l in f:
                lines.append(self.re_whitespace.split(l.strip()))
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
