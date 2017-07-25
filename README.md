# mediocre_node_exporter - A minimal node_exporter reimplementation

mediocre_node_exporter is a quick-and-dirty reimplementation of some of the basic functions of [node_exporter](https://github.com/prometheus/node_exporter), written in Python.
It was written so the author could monitor a pair of G4 Mac Minis running Linux, as Go (which node_exporter is written in) is [not supported on powerpc32 platforms](https://golang.org/doc/install/source#introduction).

mediocre_node_exporter should run on any platform supported by Python 3, but the only platform which will likely produce useful metrics is Linux.
For example, FreeBSD and OS X platforms will only return time, uname and loadavg metrics.
Windows will only return time and uname metrics.

You are welcome to file bugs (or more usefully, patches), but please keep in mind that this is not meant to be a 100% clone of node_exporter, either in usage or in functionality, though the metric names, labels and values which *are* exported are meant to be drop-in compatible with a node_exporter implementation.

## Metrics supported

* conntrack: Netfilter nf_conntrack metrics
    * node_nf_conntrack_entries
    * node_nf_conntrack_entries_limit
* diskstats: `/proc/diskstats`-based metrics
    * node_disk_*
* entropy: Kernel entropy metrics
    * node_entropy_available_bits
* filefd: File descriptor metrics
    * node_filefd_allocated
    * node_filefd_maximum
* filesystem: Filesystem metrics
    * node_filesystem_*
* loadavg: Load average
    * node_load1
    * node_load5
    * node_load15
* meminfo: `/proc/meminfo`-based metrics
    * node_memory_*
* netdev: Network interface metrics
    * node_network_*
* stat: `/proc/stat`-based metrics
    * node_boot_time
    * node_context_switches
    * node_cpu
    * node_forks
    * node_intr
    * node_procs_blocked
    * node_procs_running
* time: Current time
    * node_time
* uname: `uname` node information
    * node_uname_info
* vmstat: `/proc/vmstat`-based metrics
    * node_vmstat_*
