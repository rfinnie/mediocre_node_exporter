import pkgutil
import importlib
import sys
import traceback
from .. import monotonic_clock


class BaseCollector:
    output = {}
    output_raw = ''
    config = None

    def __init__(self):
        pass

    def postinit(self):
        pass

    def run(self):
        pass

    def parser_config(self, parser):
        pass


class Collectors:
    collectors = {}
    config = None
    metrics = {}
    metrics_raw = ''
    times = []
    successes = []

    def __init__(self):
        self.clock = monotonic_clock.clock
        for collector_name in collectors_available:
            try:
                collector = collectors_available[collector_name]()
            except NotImplementedError:
                continue
            except:
                traceback.print_exc(file=sys.stderr)
                continue
            self.collectors[collector_name] = collector

    def dump_metrics(self):
        self.run()

        self.metrics['node_scrape_collector_duration_seconds'] = entry(
            self.times,
            'gauge',
            'node_exporter: Duration of a collector scrape.',
        )
        self.metrics['node_scrape_collector_success'] = entry(
            self.successes,
            'gauge',
            'node_exporter: Whether a collector succeeded.',
        )

        import pprint
        pprint.pprint(self.metrics)

        output = ''
        for k in sorted(self.metrics):
            if self.metrics[k]['help']:
                output += '# HELP %s %s\n' % (k, self.metrics[k]['help'])
            output += '# TYPE %s %s\n' % (k, self.metrics[k]['type'])
            for a in self.metrics[k]['values']:
                if a[0]:
                    output += '%s{%s} %s\n' % (
                        k,
                        ','.join(
                            ['%s="%s"' % (x, a[0][x]) for x in sorted(a[0].keys())]
                        ),
                        a[1]
                    )
                else:
                    output += '%s %s\n' % (k, a[1])

        output += self.metrics_raw

        return(output)

    def set_config(self, config):
        self.config = config
        for collector in self.collectors:
            self.collectors[collector].config = self.config

    def postinit(self):
        collector_names = [x for x in self.collectors.keys()]
        for collector_name in collector_names:
            collector = self.collectors[collector_name]
            try:
                collector.postinit()
            except NotImplementedError:
                del(self.collectors[collector_name])
            except:
                traceback.print_exc(file=sys.stderr)
                del(self.collectors[collector_name])

    def run(self):
        self.metrics = {}
        self.raw_metrics = ''
        self.times = []
        self.successes = []
        for collector_name in self.collectors:
            collector = self.collectors[collector_name]
            collector.output = {}
            collector.output_raw = ''
            start_time = self.clock()
            try:
                collector.run()
            except:
                end_time = self.clock()
                self.times.append(({'collector': collector_name}, (end_time - start_time)))
                self.successes.append(({'collector': collector_name}, 0))
                traceback.print_exc(file=sys.stderr)
                continue
            end_time = self.clock()
            update_dict(self.metrics, collector.output)
            self.metrics_raw += collector.output_raw
            self.times.append(({'collector': collector_name}, (end_time - start_time)))
            self.successes.append(({'collector': collector_name}, 1))


def update_dict(source, to_merge):
    for (k, v) in to_merge.items():
        source[k] = v


def entry(values, type='gauge', help=None):
    out = {
        'values': values,
        'type': type,
        'help': help,
    }
    return(out)


collectors_available = {}
for importer, modname, ispkg in pkgutil.iter_modules(__path__, __name__ + '.'):
    module = importlib.find_loader(modname, __path__).load_module()
    name = modname.split('.')[-1]
    collectors_available[name] = module.Collector
