"""Copy selected local file paths as plain text."""
import subprocess

import gi
gi.require_version('Nautilus', '4.1')
from gi.repository import GObject, Nautilus


class CopyFilePath(GObject.GObject, Nautilus.MenuProvider):
    def get_file_items(self, files):
        paths = [file.get_location().get_path() for file in files]
        if not paths or any(path is None for path in paths):
            return []
        item = Nautilus.MenuItem(
            name='CopyFilePath::Copy',
            label='Copy File Path' if len(paths) == 1 else 'Copy File Paths',
            tip='Copy the full path as text',
        )
        item.connect('activate', self.copy_paths, paths)
        return [item]

    def copy_paths(self, _item, paths):
        subprocess.run(['wl-copy'], input='\n'.join(paths).encode(), check=True)
