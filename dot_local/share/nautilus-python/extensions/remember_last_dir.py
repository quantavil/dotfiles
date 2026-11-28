import os
import gi

gi.require_version("Nautilus", "4.1")
from gi.repository import Nautilus, GObject

STATE_DIR = os.path.expanduser("~/.local/state/nautilus")
LAST_DIR_FILE = os.path.join(STATE_DIR, "last-dir")


class RememberLastDirExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()
        os.makedirs(STATE_DIR, exist_ok=True)

    def get_background_items(self, current_folder):
        try:
            if current_folder and current_folder.get_uri_scheme() == "file":
                location = current_folder.get_location()
                if location:
                    path = location.get_path()
                    if path and os.path.isdir(path):
                        with open(LAST_DIR_FILE, "w") as f:
                            f.write(path)
        except Exception:
            pass
        return []

    def get_file_items(self, files):
        return []
