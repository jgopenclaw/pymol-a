from pymol.Qt import QtWidgets, QtGui, QtCore


class ChatPanel(QtWidgets.QWidget):

    USER_COLOR = QtGui.QColor(200, 220, 250)
    BOT_COLOR = QtGui.QColor(240, 240, 240)
    ERROR_COLOR = QtGui.QColor(255, 200, 200)

    def __init__(self, parent=None, pymol_instance=None):
        super().__init__(parent)
        self.pymol_instance = pymol_instance
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.chat_browser = QtWidgets.QTextBrowser()
        self.chat_browser.setOpenExternalLinks(True)
        self.chat_browser.setStyleSheet("QTextBrowser { background-color: white; }")
        layout.addWidget(self.chat_browser)

        input_layout = QtWidgets.QHBoxLayout()
        input_layout.setSpacing(4)

        self.input_edit = QtWidgets.QLineEdit()
        self.input_edit.setPlaceholderText("Type a message...")
        self.input_edit.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.input_edit, 1)

        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    def _on_send(self):
        text = self.input_edit.text().strip()
        if text:
            self.input_edit.clear()
            if hasattr(self, '_on_message_sent'):
                self._on_message_sent(text)

    def add_user_message(self, text: str):
        self._add_message(text, self.USER_COLOR, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

    def add_bot_message(self, text: str):
        self._add_message(text, self.BOT_COLOR, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

    def add_error_message(self, text: str):
        self._add_message(text, self.ERROR_COLOR, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

    def _add_message(self, text: str, background_color: QtGui.QColor, alignment: QtCore.Qt.AlignmentFlag):
        cursor = self.chat_browser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        block_format = QtGui.QTextBlockFormat()
        block_format.setAlignment(alignment)
        block_format.setTopMargin(4)
        block_format.setBottomMargin(4)
        block_format.setLeftMargin(8)
        block_format.setRightMargin(8)

        cursor.insertBlock(block_format)

        char_format = QtGui.QTextCharFormat()
        char_format.setBackground(background_color)
        char_format.setForeground(QtGui.QColor(0, 0, 0))

        cursor.insertText(text, char_format)

        self.chat_browser.setTextCursor(cursor)
        self.chat_browser.ensureCursorVisible()

    def clear_chat(self):
        self.chat_browser.clear()
