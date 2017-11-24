from . import BaseCollector, entry
import os
import re
import shlex


class Collector(BaseCollector):
    def postinit(self):
        if not self.config.textfile_directory:
            raise NotImplementedError
        self.re_series = re.compile('^([a-zA-Z_:][a-zA-Z0-9_:]+)(\{.*?\})? ([0-9\-\+e\.]+)$', re.M)
        self.re_comments = re.compile('^\# ([A-Z][A-Z0-9]+) ([a-zA-Z_:][a-zA-Z0-9_:]+) (.*?)?$', re.M)

    def parse_text(self, text, runseries):
        for (mname, mlabels, mval) in self.re_series.findall(text):
            if mname not in runseries:
                runseries[mname] = {
                    'labels': [],
                    'type': 'gauge',
                    'help': None,
                }
            lexer = shlex.shlex(mlabels[1:-1], posix=True)
            lexer.whitespace_split = True
            lexer.whitespace = ','
            runseries[mname]['labels'].append(
                (
                    dict(pair.split('=', 1) for pair in lexer),
                    float(mval),
                )
            )
        for (mtype, mname, mrest) in self.re_comments.findall(text):
            if mname not in runseries:
                runseries[mname] = {
                    'labels': [],
                    'type': 'gauge',
                    'help': None,
                }
            if mtype == 'HELP':
                runseries[mname]['help'] = mrest
            elif mtype == 'TYPE':
                runseries[mname]['type'] = mrest

    def run(self):
        runseries = {}
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
                        int(os.path.getmtime(os.path.join(path, fn)))
                ))
                with open(os.path.join(path, fn)) as f:
                    self.parse_text(f.read(), runseries)
            except (IOError, OSError):
                scrape_error = 1
                continue
        for mname in runseries:
            if not runseries[mname]['labels']:
                continue
            out[mname] = entry(
                runseries[mname]['labels'],
                runseries[mname]['type'],
                runseries[mname]['help'],
            )
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
            '-collector.textfile.directory', type=str, default=None,
            dest='textfile_directory',
            help='directory to read text files with metrics from',
        )
