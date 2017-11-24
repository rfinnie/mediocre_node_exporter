from . import BaseCollector, entry
import platform
import socket


class Collector(BaseCollector):
    def run(self):
        out = {}
        uname = platform.uname()
        domainname = ''
        try:
            domainname = '.'.join(
                socket.getaddrinfo(
                    uname[1], 0, flags=socket.AI_CANONNAME
                )[0][3].split('.')[1:]
            )
        except:
            pass
        if not domainname:
            domainname = '(none)'
        labels = {
            'sysname': uname[0],
            'nodename': uname[1],
            'release': uname[2],
            'version': uname[3],
            'machine': uname[4],
            'domainname': domainname,
        }
        out['node_uname_info'] = entry(
            [(labels, 1)],
            'gauge',
            'Labeled system information as provided by the uname system call.',
        )
        self.output = out
