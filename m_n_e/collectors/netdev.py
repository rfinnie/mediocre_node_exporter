from . import BaseCollector, entry
import os
import re


class Collector(BaseCollector):
    def postinit(self):
        if not os.path.exists(os.path.join(self.config.sysfs, 'class/net')):
            raise NotImplementedError
        self.re_ignored_devices = re.compile(self.config.netdev_ignored_devices)

    def run(self):
        out = {}
        interfaces = os.listdir(os.path.join(self.config.sysfs, 'class/net'))
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
                if self.re_ignored_devices.match(iface):
                    continue
                labels = {
                    'device': iface,
                }
                if not statmap[statkey]:
                    val = 0
                elif not os.path.exists('%s/class/net/%s/statistics/%s' % (self.config.sysfs, iface, statmap[statkey])):
                    val = 0
                else:
                    with open('%s/class/net/%s/statistics/%s' % (self.config.sysfs, iface, statmap[statkey])) as f:
                        val = int(f.read().rstrip())
                values.append((labels, val))
            out['node_network_%s' % statkey] = entry(
                values,
                'gauge',
                'Network device statistic %s.' % statkey,
            )
        self.output = out

    def parser_config(self, parser):
        parser.add_argument(
            '-collector.netdev.ignored-devices', '--collector.netdev.ignored-devices', type=str,
            default='^$',
            dest='netdev_ignored_devices',
            help='Regexp of net devices to ignore for netdev collector.',
        )
