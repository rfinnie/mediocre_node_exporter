from . import BaseCollector, entry
import os


class Collector(BaseCollector):
    def postinit(self):
        if not os.path.exists(os.path.join(self.config.procfs, 'stat')):
            raise NotImplementedError

    def run(self):
        out = {}
        statdata = {}
        with open(os.path.join(self.config.procfs, 'stat')) as f:
            for l in f:
                llist = l.rstrip().split(' ')
                k = llist.pop(0)
                statdata[k] = llist

        cpu_modes = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice']
        cpu_values = []
        for st in statdata:
            if not st.startswith('cpu'):
                continue
            if st == 'cpu':
                continue
            for i in range(len(cpu_modes)):
                try:
                    cpu_values.append(({'cpu': st, 'mode': cpu_modes[i]}, int(statdata[st][i])))
                except IndexError:
                    continue
        out['node_cpu'] = entry(
            cpu_values,
            'counter',
            'Seconds the cpus spent in each mode.',
        )
        out['node_boot_time'] = entry(
            [({}, int(statdata['btime'][0]))],
            'gauge',
            'Node boot time, in unixtime.',
        )
        out['node_intr'] = entry(
            [({}, int(statdata['intr'][0]))],
            'counter',
            'Total number of interrupts serviced.',
        )
        out['node_context_switches'] = entry(
            [({}, int(statdata['ctxt'][0]))],
            'counter',
            'Total number of context switches.',
        )
        out['node_forks'] = entry(
            [({}, int(statdata['processes'][0]))],
            'counter',
            'Total number of forks.',
        )
        out['node_procs_blocked'] = entry(
            [({}, int(statdata['procs_blocked'][0]))],
            'gauge',
            'Number of processes blocked waiting for I/O to complete.',
        )
        out['node_procs_running'] = entry(
            [({}, int(statdata['procs_running'][0]))],
            'gauge',
            'Number of processes in runnable state.',
        )
        self.output = out
