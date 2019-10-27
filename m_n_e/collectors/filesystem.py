from . import BaseCollector, entry
import os
import re


class Collector(BaseCollector):
    def postinit(self):
        if not os.path.exists(os.path.join(self.config.procfs, 'mounts')):
            raise NotImplementedError
        self.re_ignored_fs_types = re.compile(self.config.filesystem_ignored_fs_types)
        self.re_ignored_mount_points = re.compile(self.config.filesystem_ignored_mount_points)

    def run(self):
        out = {}
        values_available = []
        values_files = []
        values_files_free = []
        values_free = []
        values_readonly = []
        values_size = []
        mounts = []
        with open(os.path.join(self.config.procfs, 'mounts')) as f:
            for l in f:
                mounts.append(l.rstrip().split(' '))
        for l in mounts:
            # /proc/mounts entry can be e.g. /media/foo\040bar'
            mount = l[1].encode('utf-8').decode('unicode_escape')
            if self.re_ignored_mount_points.match(mount):
                continue
            if self.re_ignored_fs_types.match(l[2]):
                continue
            try:
                vfs = os.statvfs(mount)
            except PermissionError:
                continue
            labels = {
                'device': l[0],
                'fstype': l[2],
                'mountpoint': mount,
            }
            if l[3].startswith('ro'):
                readonly = 1
            else:
                readonly = 0

            values_available.append((labels, vfs.f_bavail * vfs.f_bsize))
            values_files.append((labels, vfs.f_files))
            values_files_free.append((labels, vfs.f_ffree))
            values_free.append((labels, vfs.f_bfree * vfs.f_bsize))
            values_readonly.append((labels, readonly))
            values_size.append((labels, vfs.f_blocks * vfs.f_bsize))
        out['node_filesystem_avail'] = entry(
            values_available,
            'gauge',
            'Filesystem space available to non-root users in bytes.',
        )
        out['node_filesystem_files'] = entry(
            values_files,
            'gauge',
            'Filesystem total file nodes.',
        )
        out['node_filesystem_files_free'] = entry(
            values_files_free,
            'gauge',
            'Filesystem total free file nodes.',
        )
        out['node_filesystem_free'] = entry(
            values_free,
            'gauge',
            'Filesystem free space in bytes.',
        )
        out['node_filesystem_readonly'] = entry(
            values_readonly,
            'gauge',
            'Filesystem read-only status.',
        )
        out['node_filesystem_size'] = entry(
            values_size,
            'gauge',
            'Filesystem size in bytes.',
        )
        self.output = out

    def parser_config(self, parser):
        parser.add_argument(
            '-collector.filesystem.ignored-fs-types', '--collector.filesystem.ignored-fs-types', type=str,
            default='^(sys|proc|auto)fs$',
            dest='filesystem_ignored_fs_types',
            help='Regexp of filesystem types to ignore for filesystem collector.',
        )
        parser.add_argument(
            '-collector.filesystem.ignored-mount-points', '--collector.filesystem.ignored-mount-points', type=str,
            default='^/(sys|proc|dev)($|/)',
            dest='filesystem_ignored_mount_points',
            help='Regexp of mount points to ignore for filesystem collector.',
        )
