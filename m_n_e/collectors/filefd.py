from . import BaseCollector, entry
import os


class Collector(BaseCollector):
    def postinit(self):
        if not os.path.exists(os.path.join(self.config.procfs, 'sys/fs/file-nr')):
            raise NotImplementedError

    def run(self):
        out = {}
        with open(os.path.join(self.config.procfs, 'sys/fs/file-nr')) as f:
            fdlist = f.read().rstrip().split('\t')
        out['node_filefd_allocated'] = entry(
            [({}, int(fdlist[0]))],
            'gauge',
            'File descriptor statistics: allocated.',
        )
        out['node_filefd_maximum'] = entry(
            [({}, int(fdlist[2]))],
            'gauge',
            'File descriptor statistics: maximum.',
        )
        self.output = out
