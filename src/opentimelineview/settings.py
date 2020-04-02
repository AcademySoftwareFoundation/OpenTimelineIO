VIEW_STYLESHEET = """
QMainWindow {
    background-color: rgb(27, 27, 27);
}

QScrollBar:horizontal {
    background: rgb(21, 21, 21);
    height: 15px;
    margin: 0px 20px 0 20px;
}

QScrollBar::handle:horizontal {
    background: rgb(255, 83, 112);
    min-width: 20px;
}

QScrollBar::add-line:horizontal {
    background: rgb(33, 33, 33);
    width: 20px;
    subcontrol-position: right;
    subcontrol-origin: margin;
}

QScrollBar::sub-line:horizontal {
    background: rgb(33, 33, 33);
    width: 20px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}

QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
    width: 3px;
    height: 3px;
    background: transparent;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

QScrollBar:vertical {
    background: rgb(21, 21, 21);
    width: 15px;
    margin: 22px 0 22px 0;
}

QScrollBar::handle:vertical {
    background: rgb(255, 83, 112);
    min-height: 20px;
}

QScrollBar::add-line:vertical {
    background: rgb(33, 33, 33);
    height: 20px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}

QScrollBar::sub-line:vertical {
    background: rgb(33, 33, 33);
    height: 20px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}

QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    width: 3px;
    height: 3px;
    background: transparent;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""
