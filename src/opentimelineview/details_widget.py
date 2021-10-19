# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from PySide2 import QtWidgets, QtGui, QtCore

import opentimelineio as otio


class Details(QtWidgets.QTextEdit):
    """Text widget with the JSON string of the specified OTIO object."""

    def __init__(self, *args, **kwargs):
        super(Details, self).__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.font = QtGui.QFontDatabase.systemFont(
            QtGui.QFontDatabase.FixedFont)
        self.font.setPointSize(12)
        self.setFont(self.font)

        self.backgroundColor = QtGui.QColor(33, 33, 33)
        self.textColor = QtGui.QColor(180, 180, 180)
        self.highlightColor = QtGui.QColor(255, 198, 109)
        self.keywordColor = QtGui.QColor(204, 120, 50)

        self.palette = QtGui.QPalette()
        self.palette.setColor(QtGui.QPalette.Base, self.backgroundColor)
        self.palette.setColor(QtGui.QPalette.Text, self.textColor)
        self.palette.setColor(QtGui.QPalette.BrightText, self.highlightColor)
        self.palette.setColor(QtGui.QPalette.Link, self.keywordColor)
        self.setPalette(self.palette)

        self.highlighter = OTIOSyntaxHighlighter(self.palette, self.document())

    def set_item(self, item):
        if item is None:
            self.setPlainText('')
        else:
            s = otio.adapters.write_to_string(item, 'otio_json')
            self.setPlainText(s)


class OTIOSyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, palette, parent=None):
        super(OTIOSyntaxHighlighter, self).__init__(parent)

        self.punctuation_format = QtGui.QTextCharFormat()
        self.punctuation_format.setForeground(palette.link())
        self.punctuation_format.setFontWeight(QtGui.QFont.Bold)

        self.key_format = QtGui.QTextCharFormat()
        # self.key_format.setFontItalic(True)

        self.literal_format = QtGui.QTextCharFormat()
        self.literal_format.setForeground(palette.brightText())
        self.literal_format.setFontWeight(QtGui.QFont.Bold)

        self.value_format = QtGui.QTextCharFormat()
        self.value_format.setForeground(palette.brightText())
        self.value_format.setFontWeight(QtGui.QFont.Bold)

        self.schema_format = QtGui.QTextCharFormat()
        self.schema_format.setForeground(QtGui.QColor(161, 194, 97))
        self.schema_format.setFontWeight(QtGui.QFont.Bold)

    def highlightBlock(self, text):
        expression = QtCore.QRegExp("(\\{|\\}|\\[|\\]|\\:|\\,)")
        index = expression.indexIn(text)
        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length, self.punctuation_format)
            index = expression.indexIn(text, index + length)

        text.replace("\\\"", "  ")

        expression = QtCore.QRegExp("\".*\" *\\:")
        expression.setMinimal(True)
        index = expression.indexIn(text)
        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length - 1, self.key_format)
            index = expression.indexIn(text, index + length)

        expression = QtCore.QRegExp("\\: *\".*\"")
        expression.setMinimal(True)
        index = expression.indexIn(text)
        while index >= 0:
            length = expression.matchedLength()
            firstQuoteIndex = text.index('"', index)
            valueLength = length - (firstQuoteIndex - index) - 2
            self.setFormat(firstQuoteIndex + 1, valueLength, self.value_format)
            index = expression.indexIn(text, index + length)

        expression = QtCore.QRegExp(r"\\: (null|true|false|[0-9\.]+)")
        index = expression.indexIn(text)
        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length, self.literal_format)
            index = expression.indexIn(text, index + length)

        expression = QtCore.QRegExp(r"\"OTIO_SCHEMA\"\s*:\s*\".*\"")
        index = expression.indexIn(text)
        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length, self.schema_format)
            index = expression.indexIn(text, index + length)
