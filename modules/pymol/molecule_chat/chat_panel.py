from pymol.Qt import QtWidgets, QtGui, QtCore

from .llm_client import get_llm_client
from . import command_translator
from . import executor
from . import screenshot


class ChatPanel(QtWidgets.QWidget):

    USER_COLOR = QtGui.QColor(200, 220, 250)
    BOT_COLOR = QtGui.QColor(240, 240, 240)
    ERROR_COLOR = QtGui.QColor(255, 200, 200)

    def __init__(self, parent=None, pymol_instance=None):
        super().__init__(parent)
        self.pymol_instance = pymol_instance
        self.llm_client = get_llm_client()
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
            self.add_user_message(text)
            self._process_message(text)

    def _process_message(self, user_input: str):
        self.send_button.setEnabled(False)
        self.add_bot_message("Thinking...")
        self._thinking_cursor = len(self.chat_browser.toPlainText())

        try:
            context = ""
            if self.pymol_instance:
                from pymol import cmd as pymol_cmd
                context = command_translator.get_current_context(pymol_cmd)

            commands = command_translator.translate_to_pymol(user_input, context)

            results = []
            if self.pymol_instance:
                from pymol import cmd as pymol_cmd
                for cmd in commands:
                    output, success = executor.execute_command(cmd, pymol_cmd)
                    results.append({
                        "command": cmd,
                        "output": output,
                        "success": success
                    })

                screenshot.capture_screenshot(pymol_cmd)

            self._remove_thinking_indicator()
            self._display_results(commands, results)

        except Exception as e:
            self._remove_thinking_indicator()
            self.add_error_message(f"Error: {str(e)}")
        finally:
            self.send_button.setEnabled(True)

    def _remove_thinking_indicator(self):
        cursor = self.chat_browser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()

    def _display_results(self, commands: list, results: list):
        if not commands:
            self.add_bot_message("No commands generated.")
            return

        response_lines = []
        for r in results:
            if r["success"]:
                response_lines.append(f"✓ {r['command']}")
            else:
                response_lines.append(f"✗ {r['command']}: {r['output']}")

        self.add_bot_message("\n".join(response_lines))

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
