#!/usr/bin/env python3

# mediocre_node_exporter - A minimal node_exporter reimplementation
# Copyright (C) 2017-2019 Ryan Finnie
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import gzip
import io
import os
import shlex
import socket
import sys
import urllib

from . import collectors

COLLECTORS = None
INDEX_PAGE_CONTENT = """<html>
<head><title>Mediocre Node Exporter</title></head>
<body>
<h1>Mediocre Node Exporter</h1>
<p><a href="{telemetry_path}">Metrics</a></p>
</body>
</html>"""


def parse_args(argv, collectors):
    import argparse

    parser = argparse.ArgumentParser(
        description='mediocre_node_exporter',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-web.listen-address', '--web.listen-address', type=str, default=':9100',
        dest='listen_address',
        help='address on which to expose metrics and web interface',
    )
    parser.add_argument(
        '-web.telemetry-path', '--web.telemetry-path', type=str, default='/metrics',
        dest='telemetry_path',
        help='path under which to expose metrics',
    )
    parser.add_argument(
        '-dump', '--dump', action='store_true',
        help='do not start web server, just dump stats',
    )

    collector_names = ','.join(sorted(collectors.keys()))
    parser.add_argument(
        '-collectors.enabled', '--collectors.enabled', type=str, default=collector_names,
        dest='collectors_enabled',
        help='Comma-separated list of collectors to use.',
    )
    parser.add_argument(
        '-collectors.print', '--collectors.print', action='store_true',
        dest='collectors_print',
        help='If true, print available collectors and exit.',
    )
    parser.add_argument(
        '-collector.procfs', '--collector.procfs', type=str, default='/proc',
        dest='procfs',
        help='procfs mountpoint.',
    )
    parser.add_argument(
        '-collector.sysfs', '--collector.sysfs', type=str, default='/sys',
        dest='sysfs',
        help='sysfs mountpoint.',
    )

    for collector_name in collectors:
        collector = collectors[collector_name]
        collector.parser_config(parser)

    return parser.parse_args(argv[1:])


class ServerApplication():
    environ = None
    query_params = None
    start_response = None

    def process_response(self, output, headers):
        if 'gzip' in self.environ.get('HTTP_ACCEPT_ENCODING', ''):
            zbuf = io.BytesIO()
            zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
            zfile.write(output.encode('UTF-8'))
            zfile.close()
            output = zbuf.getvalue()
            headers['Content-Encoding'] = 'gzip'
        else:
            output = output.encode('UTF-8')
        headers['Content-Length'] = str(len(output))
        return output, list(headers.items())

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        self.query_params = {}
        if 'QUERY_STRING' in self.environ:
            self.query_params = urllib.parse.parse_qs(self.environ['QUERY_STRING'])
        if self.environ['REQUEST_METHOD'] == 'GET':
            return self.do_GET()
        else:
            body, headers = self.process_response(
                'Method Not Allowed',
                {'Content-Type': 'text/plain; charset=utf-8'},
            )
            self.start_response('405 Method Not Allowed', headers)
            return [body]

    def do_GET(self):
        if self.environ['PATH_INFO'] == COLLECTORS.config.telemetry_path:
            body, headers = self.process_response(
                COLLECTORS.dump_metrics(),
                {'Content-Type': 'text/plain; version=0.0.4'},
            )
            self.start_response('200 OK', headers)
            return [body]
        elif self.environ['PATH_INFO'] == '/':
            body, headers = self.process_response(
                INDEX_PAGE_CONTENT.format.format(
                    telemetry_path=COLLECTORS.config.telemetry_path,
                ),
                {'Content-Type': 'text/html; charset=utf-8'},
            )
            self.start_response('200 OK', headers)
            return [body]
        else:
            body, headers = self.process_response(
                'Not Found',
                {'Content-Type': 'text/plain; charset=utf-8'},
            )
            self.start_response('404 Not Found', headers)
            return [body]


def load_config(argv=None):
    global CONFIG
    global COLLECTORS

    cmdline = os.environ.get('MNE_CMDLINE')
    if cmdline:
        argv = [''] + shlex.split(cmdline)
    if not argv:
        argv = ['']

    COLLECTORS = collectors.Collectors()
    CONFIG = parse_args(argv, COLLECTORS.collectors)
    collectors_enabled = CONFIG.collectors_enabled.split(',')
    COLLECTORS.set_config(CONFIG)
    COLLECTORS.postinit()
    all_collectors = sorted([x for x in COLLECTORS.collectors.keys()])
    if CONFIG.collectors_print:
        print('Available collectors:')
        for collector_name in all_collectors:
            print('- {}'.format(collector_name))
        return
    for collector in all_collectors:
        if collector not in collectors_enabled:
            del(COLLECTORS.collectors[collector])


def main():
    global CONFIG
    global COLLECTORS

    load_config(sys.argv)

    if CONFIG.dump:
        sys.stdout.write(COLLECTORS.dump_metrics())
        return

    from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler

    class WSGIServerV6(WSGIServer):
        address_family = socket.AF_INET6

    class RequestHandler(WSGIRequestHandler):
        def address_string(self):
            if (self.server.address_family == socket.AF_INET6) and self.client_address[0].startswith('::ffff:'):
                return self.client_address[0][7:]
            return self.client_address[0]

    server_port = int(CONFIG.listen_address.split(':')[-1])
    server_host = ':'.join(CONFIG.listen_address.split(':')[:-1])
    if server_host == '':
        test_addrinfo = socket.getaddrinfo(None, server_port)[0]
        if test_addrinfo[0] == socket.AF_INET6:
            server_host = '::'
        else:
            server_host = '0.0.0.0'
    if (server_host[0] == '[') and (server_host[-1] == ']'):
        server_host = server_host[1:-1]
    server_addrinfo = socket.getaddrinfo(server_host, server_port)[0]
    if server_addrinfo[0] == socket.AF_INET6:
        server_class = WSGIServerV6
    else:
        server_class = WSGIServer

    handler = ServerApplication()
    httpd = make_server(server_host, server_port, handler, server_class, RequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    sys.exit(main())
