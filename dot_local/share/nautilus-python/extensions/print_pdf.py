"""Add a PDF print action to GNOME Files."""
import os
import subprocess
import gi

gi.require_version("Nautilus", "4.1")
from gi.repository import GObject, Nautilus


class PrintPdfExtension(GObject.GObject, Nautilus.MenuProvider):
    def get_file_items(self, files):
        if len(files) != 1 or files[0].get_mime_type() != "application/pdf":
            return []
        path = files[0].get_location().get_path()
        if not path or not os.path.isfile(path):
            return []
        item = Nautilus.MenuItem(name="PrintPdf::print", label="Print…", tip="Choose a printer and print this PDF")
        item.connect("activate", lambda _item: subprocess.Popen([os.path.expanduser("~/.local/bin/nautilus-print-pdf"), path]))
        return [item]
