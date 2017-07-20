from PySide import QtGui

import opentimelineio as otio

class Details(QtGui.QTextEdit):

    def __init__(self, *args, **kwargs):
        super(Details, self).__init__(*args, **kwargs)
        self.setFixedHeight(100)

    def set_item(self, item):
        if item is None:
            self.setPlainText('')
        else:
            s = otio.adapters.write_to_string(item, 'otio_json')
            self.setPlainText(s)
