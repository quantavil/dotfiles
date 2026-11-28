"""Run an executable shell script in a visible terminal."""
import os
import subprocess

import gi
gi.require_version('Nautilus', '4.1')
from gi.repository import GObject, Nautilus


class RunScriptInTerminal(GObject.GObject, Nautilus.MenuProvider):
    def get_file_items(self, files):
        if len(files) != 1:
            return []
        path = files[0].get_location().get_path()
        if not path or not path.endswith('.sh') or not os.path.isfile(path) or not os.access(path, os.X_OK):
            return []
        item = Nautilus.MenuItem(name='RunScriptInTerminal::Run',
                                 label='Run Script in Terminal',
                                 tip='Run this script and show its output')
        item.connect('activate', self.run_script, path)
        return [item]

    def run_script(self, _item, path):
        subprocess.Popen(['rio', '-e', 'bash', '-c',
                          '"$1"; code=$?; printf "\\nFinished (exit code %s). Press Enter to close.\\n" "$code"; read -r; exit "$code"',
                          '_', path])
