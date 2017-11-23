from . import BaseCollector, entry
import platform


class Collector(BaseCollector):
    def run(self):
        out = {}
        uname = platform.uname()
        labels = {
            'sysname': uname[0],
            'nodename': uname[1],
            'release': uname[2],
            'version': uname[3],
            'machine': uname[4],
            'domainname': '(none)',
        }
        out['node_uname_info'] = entry(
            [(labels, 1)],
            'gauge',
            'Labeled system information as provided by the uname system call.',
        )
        self.output = out
