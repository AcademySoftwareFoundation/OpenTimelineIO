# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

try:
    from PySide6 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore

import opentimelineio as otio


class Details(QtWidgets.QTextEdit):
    """Text widget with the JSON string of the specified OTIO object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        super().__init__(parent)

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
        expression = QtCore.QRegularExpression("(\\{|\\}|\\[|\\]|\\:|\\,)")
        match = expression.match(text)
        index = match.capturedStart()
        while index >= 0:
            length = match.capturedLength()
            self.setFormat(index, length, self.punctuation_format)
            match = expression.match(text, index + length)
            index = match.capturedStart()

        text.replace("\\\"", "  ")

        expression = QtCore.QRegularExpression(
            "\".*\" *\\:",
            QtCore.QRegularExpression.InvertedGreedinessOption)
        match = expression.match(text)
        index = match.capturedStart()
        while index >= 0:
            length = match.capturedLength()
            self.setFormat(index, length - 1, self.key_format)
            match = expression.match(text, index + length)
            index = match.capturedStart()

        expression = QtCore.QRegularExpression(
            "\\: *\".*\"",
            QtCore.QRegularExpression.InvertedGreedinessOption)
        match = expression.match(text)
        index = match.capturedStart()
        while index >= 0:
            length = match.capturedLength()
            firstQuoteIndex = text.index('"', index)
            valueLength = length - (firstQuoteIndex - index) - 2
            self.setFormat(firstQuoteIndex + 1, valueLength, self.value_format)
            match = expression.match(text, index + length)
            index = match.capturedStart()

        expression = QtCore.QRegularExpression(r"\\: (null|true|false|[0-9\.]+)")
        match = expression.match(text)
        index = match.capturedStart()
        while index >= 0:
            length = match.capturedLength()
            self.setFormat(index, length, self.literal_format)
            match = expression.match(text, index + length)
            index = match.capturedStart()

        expression = QtCore.QRegularExpression(r"\"OTIO_SCHEMA\"\s*:\s*\".*\"")
        match = expression.match(text)
        index = match.capturedStart()
        while index >= 0:
            length = match.capturedLength()
            self.setFormat(index, length, self.schema_format)
            match = expression.match(text, index + length)
            index = match.capturedStart()
