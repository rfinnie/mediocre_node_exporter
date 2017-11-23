from . import BaseCollector, entry
import re
import os


class Collector(BaseCollector):
    def run(self):
        if not os.path.exists('/proc/diskstats'):
            return
        out = {}
        metrics_info = [
            ('node_disk_reads_completed', 'counter', 'The total number of reads completed successfully.'),
            ('node_disk_reads_merged', 'counter', 'The total number of reads merged. See https://www.kernel.org/doc/Documentation/iostats.txt.'),
            ('node_disk_sectors_read', 'counter', 'The total number of sectors read successfully.'),
            ('node_disk_read_time_ms', 'counter', 'The total number of milliseconds spent by all reads.'),
            ('node_disk_writes_completed', 'counter', 'The total number of writes completed successfully.'),
            ('node_disk_writes_merged', 'counter', 'The number of writes merged. See https://www.kernel.org/doc/Documentation/iostats.txt.'),
            ('node_disk_sectors_written', 'counter', 'The total number of sectors written successfully.'),
            ('node_disk_write_time_ms', 'counter', 'This is the total number of milliseconds spent by all writes.'),
            ('node_disk_io_now', 'counter', 'The number of I/Os currently in progress.'),
            ('node_disk_io_time_ms', 'counter', 'Total Milliseconds spent doing I/Os.'),
            ('node_disk_io_time_weighted', 'counter', 'The weighted # of milliseconds spent doing I/Os. See https://www.kernel.org/doc/Documentation/iostats.txt.'),
            ('node_disk_bytes_read', 'counter', 'The total number of bytes read successfully.'),
            ('node_disk_bytes_written', 'counter', 'The total number of bytes written successfully.'),
        ]
        values = {}
        for (metric, metric_type, metric_help) in metrics_info:
            values[metric] = []
        diskstats = []
        with open('/proc/diskstats') as f:
            for l in f:
                diskstats.append(re.split('\s+', l.strip()))
        for l in diskstats:
            labels = {
                'device': l[2],
            }
            values['node_disk_reads_completed'].append((labels, int(l[3])))
            values['node_disk_reads_merged'].append((labels, int(l[4])))
            values['node_disk_sectors_read'].append((labels, int(l[5])))
            values['node_disk_read_time_ms'].append((labels, int(l[6])))
            values['node_disk_writes_completed'].append((labels, int(l[7])))
            values['node_disk_writes_merged'].append((labels, int(l[8])))
            values['node_disk_sectors_written'].append((labels, int(l[9])))
            values['node_disk_write_time_ms'].append((labels, int(l[10])))
            values['node_disk_io_now'].append((labels, int(l[11])))
            values['node_disk_io_time_ms'].append((labels, int(l[12])))
            values['node_disk_io_time_weighted'].append((labels, int(l[13])))
            values['node_disk_bytes_read'].append((labels, (int(l[5]) * 512)))
            values['node_disk_bytes_written'].append((labels, (int(l[9]) * 512)))
            values['node_disk_bytes_written'].append((labels, (int(l[9]) * 512)))

        for (metric, metric_type, metric_help) in metrics_info:
            out[metric] = entry(values[metric], metric_type, metric_help)
        self.output = out
