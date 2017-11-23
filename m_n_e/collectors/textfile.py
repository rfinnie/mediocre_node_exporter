from . import BaseCollector
import os


class Collector(BaseCollector):
    def run(self):
        out = ''
        path = self.config.textfile_directory
        if not path:
            return
        try:
            promfiles = [fn for fn in os.listdir(path) if os.path.isfile(os.path.join(path, fn)) and fn.endswith('.prom')]
        except (IOError, OSError):
            return
        for fn in sorted(promfiles):
            try:
                with open(os.path.join(path, fn)) as f:
                    out += f.read()
            except (IOError, OSError):
                continue
        self.output_raw = out

    def parser_config(self, parser):
        parser.add_argument(
            '-collector.textfile.directory', type=str, default=None,
            dest='textfile_directory',
            help='directory to read text files with metrics from',
        )
