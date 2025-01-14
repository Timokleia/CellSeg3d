from qtpy.QtWidgets import QTextEdit

from napari_cellseg3d.utils import LOGGER as logger


class LogFixture(QTextEdit):
    """Fixture for testing, replaces napari_cellseg3d.interface.Log in model_workers during testing"""

    def __init__(self):
        super(LogFixture, self).__init__()

    def print_and_log(self, text, printing=None):
        print(text)

    def warn(self, warning):
        logger.warning(warning)

    def error(self, e):
        raise (e)
