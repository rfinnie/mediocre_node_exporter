from . import BaseCollector, entry
import os
import re


class Collector(BaseCollector):
    def __init__(self):
        if not os.path.exists('/proc/mounts'):
            raise NotImplementedError

    def run(self):
        out = {}
        re_ignored_fs_types = re.compile(self.config.filesystem_ignored_fs_types)
        re_ignored_mount_points = re.compile(self.config.filesystem_ignored_mount_points)
        values_available = []
        values_files = []
        values_files_free = []
        values_free = []
        values_readonly = []
        values_size = []
        mounts = []
        with open('/proc/mounts') as f:
            for l in f:
                mounts.append(l.rstrip().split(' '))
        for l in mounts:
            if re_ignored_mount_points.match(l[1]):
                continue
            if re_ignored_fs_types.match(l[2]):
                continue
            mount = l[1]
            vfs = os.statvfs(mount)
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
            '-collector.filesystem.ignored-fs-types', type=str,
            default='^(sys|proc|auto)fs$',
            dest='filesystem_ignored_fs_types',
            help='Regexp of filesystem types to ignore for filesystem collector.',
        )
        parser.add_argument(
            '-collector.filesystem.ignored-mount-points', type=str,
            default='^/(sys|proc|dev)($|/)',
            dest='filesystem_ignored_mount_points',
            help='Regexp of mount points to ignore for filesystem collector.',
        )
