from . import BaseCollector, entry
from .. import version


class Collector(BaseCollector):
    def run(self):
        out = {}
        labels = {
            'implementation': 'mediocre_node_exporter',
            'version': version.VERSION,
            'pyversion': version.PYTHON_VERSION,
        }
        if version.GIT_BRANCH:
            labels['branch'] = version.GIT_BRANCH
        if version.GIT_REVISION:
            labels['revision'] = version.GIT_REVISION
        out['node_exporter_build_info'] = entry(
            [(labels, 1)],
            'gauge',
            "A metric with a constant '1' value with build/runtime information.",
        )
        self.output = out
