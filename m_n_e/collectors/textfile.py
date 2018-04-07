from . import BaseCollector, entry, TextParser
import os


class Collector(BaseCollector):
    def postinit(self):
        if not self.config.textfile_directory:
            raise NotImplementedError

    def run(self):
        parser = TextParser()
        out = {}
        mtimes = []
        scrape_error = 0
        path = self.config.textfile_directory
        if not path:
            return
        try:
            promfiles = [fn for fn in os.listdir(path) if os.path.isfile(os.path.join(path, fn)) and fn.endswith('.prom')]
        except (IOError, OSError):
            scrape_error = 1
            promfiles = []
        for fn in sorted(promfiles):
            try:
                mtimes.append((
                        {'file': fn},
                        os.path.getmtime(os.path.join(path, fn))
                ))
                with open(os.path.join(path, fn)) as f:
                    parser.parse(f.read())
            except (IOError, OSError):
                scrape_error = 1
                continue
        for mname, mvalue in parser.dump().items():
            out[mname] = mvalue
        out['node_textfile_mtime'] = entry(
            mtimes,
            'gauge',
            'Unixtime mtime of textfiles successfully read.',
        )
        out['node_textfile_scrape_error'] = entry(
            [({}, scrape_error)],
            'gauge',
            '1 if there was an error opening or reading a file, 0 otherwise',
        )
        self.output = out

    def parser_config(self, parser):
        parser.add_argument(
            '-collector.textfile.directory', '--collector.textfile.directory', type=str, default=None,
            dest='textfile_directory',
            help='directory to read text files with metrics from',
        )
