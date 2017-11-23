from . import BaseCollector, entry
import os


class Collector(BaseCollector):
    def run(self):
        out = {}
        interfaces = os.listdir('/sys/class/net')
        statmap = {
            'receive_bytes': 'rx_bytes',
            'receive_compressed': 'rx_compressed',
            'receive_drop': 'rx_dropped',
            'receive_errs': 'rx_errors',
            'receive_fifo': 'rx_fifo_errors',
            'receive_frame': 'rx_frame_errors',
            'receive_multicast': 'multicast',
            'receive_packets': 'rx_packets',
            'transmit_bytes': 'tx_bytes',
            'transmit_compressed': 'tx_compressed',
            'transmit_drop': 'tx_dropped',
            'transmit_errs': 'tx_errors',
            'transmit_fifo': 'tx_fifo_errors',
            'transmit_frame': 'tx_frame_errors',
            'transmit_multicast': None,
            'transmit_packets': 'tx_packets',
        }

        for statkey in sorted(statmap):
            values = []
            for iface in interfaces:
                labels = {
                    'device': iface,
                }
                if not statmap[statkey]:
                    val = 0
                elif not os.path.exists('/sys/class/net/%s/statistics/%s' % (iface, statmap[statkey])):
                    val = 0
                else:
                    with open('/sys/class/net/%s/statistics/%s' % (iface, statmap[statkey])) as f:
                        val = int(f.read().rstrip())
                values.append((labels, val))
            out['node_network_%s' % statkey] = entry(
                values,
                'gauge',
                'Network device statistic %s.' % statkey,
            )
        self.output = out
