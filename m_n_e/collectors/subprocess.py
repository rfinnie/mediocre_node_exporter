from . import BaseCollector, entry, TextParser
import os
import subprocess


class Collector(BaseCollector):
    def postinit(self):
        if not self.config.subprocess_directory:
            raise NotImplementedError

    def run(self):
        parser = TextParser()
        out = {}
        exitcodes = []
        path = self.config.subprocess_directory
        if not path:
            return
        try:
            execfiles = [fn for fn in os.listdir(path) if os.path.isfile(os.path.join(path, fn)) and os.access(os.path.join(path, fn), os.X_OK)]
        except (IOError, OSError):
            execfiles = []
        for fn in sorted(execfiles):
            exitcode = 0
            try:
                parser.parse(subprocess.check_output(os.path.join(path, fn)).decode('UTF-8'))
            except subprocess.CalledProcessError as e:
                exitcode = e.returncode
            exitcodes.append((
                {'file': fn},
                exitcode
            ))
        for mname, mvalue in parser.dump().items():
            out[mname] = mvalue
        out['node_subprocess_exit_number'] = entry(
            exitcodes,
            'gauge',
            'Exit code of the executed subprocess.',
        )
        self.output = out

    def parser_config(self, parser):
        parser.add_argument(
            '-collector.subprocess.directory', '--collector.subprocess.directory', type=str, default=None,
            dest='subprocess_directory',
            help='directory to exec subprocess metrics',
        )
