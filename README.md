# mediocre_node_exporter - A minimal node_exporter reimplementation

mediocre_node_exporter is a minimal reimplementation of some of the basic functions of [node_exporter](https://github.com/prometheus/node_exporter), written in Python.
It was written so the author could monitor a pair of G4 Mac Minis running Linux, as Go (which node_exporter is written in) is [not supported on powerpc32 platforms](https://golang.org/doc/install/source#introduction).

mediocre_node_exporter should run on any platform supported by Python 3, but the only platform which will likely produce useful metrics is Linux.
For example, FreeBSD and OS X platforms will only return time, uname and loadavg metrics.
Windows will only return time and uname metrics.

You are welcome to file bugs (or more usefully, patches), but please keep in mind that this is not meant to be a 100% clone of node_exporter, either in usage or in functionality.
However, the metric names, labels and values which *are* exported are meant to be drop-in compatible with a node_exporter implementation.

## Collectors supported

* conntrack: Netfilter nf_conntrack metrics
* diskstats: `/proc/diskstats`-based metrics
* entropy: Kernel entropy metrics
* filefd: File descriptor metrics
* filesystem: Filesystem metrics
* loadavg: Load average
* meminfo: `/proc/meminfo`-based metrics
* netdev: Network interface metrics
* stat: `/proc/stat`-based metrics
* subprocess: Metrics retrieved by running executables in a specified directory (*mediocre_node_exporter extension*)
* textfile: Metrics loaded from .prom files in a specified directory
* time: Current time
* uname: `uname` node information
* version: Runtime/compiler version information (*mediocre_node_exporter extension*)
* vmstat: `/proc/vmstat`-based metrics
