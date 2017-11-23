from . import BaseCollector, entry
import os


class Collector(BaseCollector):
    def postinit(self):
        if not (
            os.path.exists(os.path.join(self.config.procfs, 'sys/net/netfilter/nf_conntrack_count')) or
            os.path.exists(os.path.join(self.config.procfs, 'sys/net/netfilter/nf_conntrack_max'))
        ):
            raise NotImplementedError

    def run(self):
        out = {}
        if os.path.exists(os.path.join(self.config.procfs, 'sys/net/netfilter/nf_conntrack_count')):
            with open(os.path.join(self.config.procfs, 'sys/net/netfilter/nf_conntrack_count')) as f:
                out['node_nf_conntrack_entries'] = entry(
                    [({}, int(f.read().rstrip()))],
                    'gauge',
                    'Number of currently allocated flow entries for connection tracking.',
                )
        if os.path.exists(os.path.join(self.config.procfs, 'sys/net/netfilter/nf_conntrack_max')):
            with open(os.path.join(self.config.procfs, 'sys/net/netfilter/nf_conntrack_max')) as f:
                out['node_nf_conntrack_entries_limit'] = entry(
                    [({}, int(f.read().rstrip()))],
                    'gauge',
                    'Maximum size of connection tracking table.',
                )
        self.output = out
