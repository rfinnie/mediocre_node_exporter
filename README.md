# mediocre_node_exporter - A minimal node_exporter reimplementation

mediocre_node_exporter is a quick-and-dirty reimplementation of some of the basic functions of [node_exporter](https://github.com/prometheus/node_exporter), written in Python.
It was written so the author could monitor a pair of G4 Mac Minis running Linux, as Go (which node_exporter is written in) is [not supported on powerpc32 platforms](https://golang.org/doc/install/source#introduction).

You are welcome to file bugs (or more usefully, patches), but please keep in mind that this is not meant to be a 100% clone of node_exporter, either in usage or in functionality, though the metric names, labels and values which *are* exported are meant to be drop-in compatible with a node_exporter implementation.

## Metrics supported

* `/proc/stat`-based metrics
    * node_boot_time
    * node_context_switches
    * node_cpu
    * node_forks
    * node_intr
    * node_procs_blocked
    * node_procs_running
* Filesystem metrics
    * node_filesystem_available
    * node_filesystem_files
    * node_filesystem_files_free
    * node_filesystem_free
    * node_filesystem_readonly
    * node_filesystem_size
* Load average
    * node_load1
    * node_load5
    * node_load15
* `/proc/meminfo`-based metrics
    * node_memory_*
* Network interface metrics
    * node_network_receive_*
    * node_network_transmit_*
