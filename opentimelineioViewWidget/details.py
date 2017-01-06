try:
    from PySide import QtGui
except:
    from PyQt4 import QtGui


class Details(QtGui.QTextEdit):

    def __init__(self, *args, **kwargs):
        super(Details, self).__init__(*args, **kwargs)
        self.setFixedHeight(100)

    def set_item(self, item):
        if item is None:
            self.setPlainText('')
        else:
            self.setPlainText(str(item))
