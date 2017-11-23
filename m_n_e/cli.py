#!/usr/bin/env python3

# mediocre_node_exporter - A minimal node_exporter reimplementation
# Copyright (C) 2017 Ryan Finnie
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

import sys
import http.server
import socket
import io
import gzip
from . import collectors

INDEX_PAGE_CONTENT = """<html>
<head><title>Mediocre Node Exporter</title></head>
<body>
<h1>Mediocre Node Exporter</h1>
<p><a href="{telemetry_path}">Metrics</a></p>
</body>
</html>"""

NOTFOUND_PAGE_CONTENT = """<html>
<head><title>404 Not Found</title></head>
<body>
<h1>Not Found</h1>
<p>The requested URL was not found on this server.</p>
</body>
</html>"""


def parse_args(collectors):
    import argparse

    parser = argparse.ArgumentParser(
        description='mediocre_node_exporter',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-web.listen-address', type=str, default=':9100',
        dest='listen_address',
        help='address on which to expose metrics and web interface',
    )
    parser.add_argument(
        '-web.telemetry-path', type=str, default='/metrics',
        dest='telemetry_path',
        help='path under which to expose metrics',
    )
    parser.add_argument(
        '-dump', action='store_true',
        help='do not start web server, just dump stats',
    )

    collector_names = ','.join(sorted(collectors.keys()))
    parser.add_argument(
        '-collectors.enabled', type=str, default=collector_names,
        dest='collectors_enabled',
        help='Comma-separated list of collectors to use.',
    )
    parser.add_argument(
        '-collectors.print', action='store_true',
        dest='collectors_print',
        help='If true, print available collectors and exit.',
    )
    parser.add_argument(
        '-collector.procfs', type=str, default='/proc',
        dest='procfs',
        help='procfs mountpoint.',
    )
    parser.add_argument(
        '-collector.sysfs', type=str, default='/sys',
        dest='sysfs',
        help='sysfs mountpoint.',
    )

    for collector_name in collectors:
        collector = collectors[collector_name]
        collector.parser_config(parser)

    return parser.parse_args()


class HTTPServerV6(http.server.HTTPServer):
    address_family = socket.AF_INET6


class NodeExporterHandler(http.server.BaseHTTPRequestHandler):
    Collectors = None

    def do_GET(self):
        if self.path == self.Collectors.config.telemetry_path:
            content = {
                'code': 200,
                'output': self.Collectors.dump_metrics(),
                'content_type': 'text/plain; version=0.0.4',
            }
        elif self.path == '/':
            content = {
                'code': 200,
                'output': INDEX_PAGE_CONTENT.format(
                    telemetry_path=self.Collectors.config.telemetry_path,
                ),
                'content_type': 'text/html; charset=utf-8',
            }
        else:
            content = {
                'code': 404,
                'output': NOTFOUND_PAGE_CONTENT,
                'content_type': 'text/html; charset=utf-8',
            }

        self.protocol_version = self.request_version
        self.send_response(content['code'])
        self.send_header('Content-Type', content['content_type'])
        output = content['output']
        if self.headers.get('Accept-Encoding') and ('gzip' in self.headers.get('Accept-Encoding')):
            zbuf = io.BytesIO()
            zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
            zfile.write(output.encode('UTF-8'))
            zfile.close()
            output = zbuf.getvalue()
            self.send_header('Content-Encoding', 'gzip')
        else:
            output = output.encode('UTF-8')
        self.send_header('Content-Length', str(len(output)))
        self.end_headers()
        self.wfile.write(output)


def main():
    Collectors = collectors.Collectors()
    config = parse_args(Collectors.collectors)
    collectors_enabled = config.collectors_enabled.split(',')
    Collectors.set_config(config)
    Collectors.postinit()
    all_collectors = sorted([x for x in Collectors.collectors.keys()])
    if config.collectors_print:
        print('Available collectors:')
        for collector_name in all_collectors:
            print('- {}'.format(collector_name))
        return
    for collector in all_collectors:
        if collector not in collectors_enabled:
            del(Collectors.collectors[collector])
    if config.dump:
        sys.stdout.write(Collectors.dump_metrics())
        return
    server_port = int(config.listen_address.split(':')[-1])
    server_host = ':'.join(config.listen_address.split(':')[:-1])
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
        server_class = HTTPServerV6
    else:
        server_class = http.server.HTTPServer
    httpd = server_class(
        (server_addrinfo[-1][0], server_addrinfo[-1][1]),
        NodeExporterHandler
    )
    httpd.RequestHandlerClass.Collectors = Collectors
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    sys.exit(main())
