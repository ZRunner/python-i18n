import os.path
import sys

from .loader import I18nFileLoadError, Loader


class PythonLoader(Loader):
    """Class to load python files"""
    def __init__(self):
        super(PythonLoader, self).__init__()

    def load_file(self, filename: str):
        path, name = os.path.split(filename)
        module_name, ext = os.path.splitext(name)
        if path not in sys.path:
            sys.path.append(path)
        try:
            return __import__(module_name)
        except ImportError:
            raise I18nFileLoadError("error loading file {0}".format(filename))

    def parse_file(self, file_content):
        return file_content

    def check_data(self, data, root_data):
        return hasattr(data, root_data)

    def get_data(self, data, root_data):
        return getattr(data, root_data)
