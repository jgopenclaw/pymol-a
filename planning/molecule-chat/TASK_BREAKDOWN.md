# MoleculeChat — Task Breakdown for Coding Agents

## Project Overview
- **Goal:** Add a conversational AI chat panel to PyMOL for natural language control
- **Location:** `/Users/openclaw/.openclaw/workspace/projects/molecule-chat/`
- **Target Repo:** `https://github.com/jgopenclaw/pymol-a`

---

## Phase 1: Project Setup & Infrastructure

### Task 1.1: Create plugin directory structure

**Location:** `modules/pymol/molecule_chat/`

**Steps:**
1. Create directory `modules/pymol/molecule_chat/`
2. Create `__init__.py` with:
   - Plugin metadata (`__plugin_name__`, `__plugin_author__`, etc.)
   - `__plugin_activate__()` and `__plugin_deactivate__()` functions
   - Import and register menu item in PyMOL's plugin menu
3. Verify plugin loads in PyMOL (add a simple "Hello" message first)
4. Commit: "Initial plugin scaffold for MoleculeChat"

**Test criteria:** Plugin appears in PyMOL menu and prints message on activation

---

### Task 1.2: Set up configuration system

**Location:** `modules/pymol/molecule_chat/config.py`

**Steps:**
1. Create `config.py` with:
   - `CONFIG_PATH = os.path.expanduser("~/.pymol/molecule_chat_config.json")`
   - `save_config(config: dict)` function
   - `load_config() -> dict` function
   - `get_api_key(provider: str) -> str` function
   - `get_provider() -> str` function (default: "openai")
2. Create default config with placeholders for API keys
3. Add method to prompt user for API key setup
4. Commit: "Add configuration system for API keys"

**Test criteria:** Config file created/read correctly, API key retrieval works

---

## Phase 2: Chat Panel UI

### Task 2.1: Create ChatPanel QWidget

**Location:** `modules/pymol/molecule_chat/chat_panel.py`

**Steps:**
1. Create `ChatPanel` class extending `QtWidgets.QWidget`
2. In `__init__`:
   - Accept `parent` and `pymol_instance` parameters
   - Set up `QVBoxLayout`
   - Create `QScrollArea` for chat history (or `QTextBrowser`)
   - Create input area: `QLineEdit` + `QPushButton` (Send)
   - Connect send button and Enter key to send message
3. Implement `add_user_message(text: str)` - right-aligned, user color
4. Implement `add_bot_message(text: str)` - left-aligned, bot color
5. Implement `add_error_message(text: str)` - red styling
6. Implement `clear_chat()` method
7. Test: Panel renders, messages appear, input works

**Test criteria:** Widget displays in PyMOL, messages render correctly

---

### Task 2.2: Integrate ChatPanel into PyMOL GUI

**Location:** Modify `modules/pmg_qt/pymol_qt_gui.py`

**Steps:**
1. Add `open_chat_panel()` method to `PyMOLQtGUI` class:
   ```python
   def open_chat_panel(self):
       from pymol.molecule_chat.chat_panel import ChatPanel
       if not hasattr(self, 'chat_panel'):
           self.chat_panel = ChatPanel(self, self.pymolwidget.pymol)
           self.addDockWidget(Qt.RightDockWidgetArea, self.chat_panel)
       self.chat_panel.show()
       self.chat_panel.raise_()
   ```
2. Add menu item: Plugins → MoleculeChat
3. Add keyboard shortcut: Ctrl+M (Cmd+M on Mac)
4. Test: Chat panel appears as docked widget on menu click

**Test criteria:** Menu item works, shortcut toggles panel, panel is dockable

---

### Task 2.3: Add screenshot display to chat

**Location:** `modules/pymol/molecule_chat/chat_panel.py`

**Steps:**
1. Add `add_screenshot(image_bytes: bytes)` method to ChatPanel
2. Use `QPixmap` to convert bytes to image
3. Display in `QLabel` with click-to-enlarge (popup dialog)
4. Auto-scroll after adding image
5. Test: Screenshot appears in chat after command

**Test criteria:** Images display correctly, thumbnail + full view works

---

## Phase 3: LLM Integration

### Task 3.1: Create LLM client abstraction

**Location:** `modules/pymol/molecule_chat/llm_client.py`

**Steps:**
1. Create abstract base class `LLMClient`:
   - `chat(messages: list[dict]) -> str`
   - `supports_vision() -> bool`
2. Create `OpenAIClient`:
   - Accept `api_key`, `model` (default: "gpt-4o")
   - Implement `chat()` using openai library
   - Support vision for image analysis
3. Create `OllamaClient`:
   - Accept `base_url` (default: "http://localhost:11434")
   - Implement `chat()` using Ollama API
4. Create factory function `get_llm_client() -> LLMClient`:
   - Read config, return appropriate client
5. Add error handling for missing API key

**Test criteria:** Both clients work, factory returns correct type

---

### Task 3.2: Implement command translator

**Location:** `modules/pymol/molecule_chat/command_translator.py`

**Steps:**
1. Create `translate_to_pymol(user_input: str, context: str) -> list[str]`:
   - Build prompt with system instructions
   - Include examples of NL → PyMOL command mapping
   - Call LLM, parse response into command list
2. Create system prompt with:
   - Role: PyMOL command translator
   - Rules: valid commands only, proper selection syntax
   - Examples: 5-10 NL → command examples
3. Add context injection (current objects, view state)
4. Parse LLM output to extract commands (split by newlines)

**Test criteria:** LLM returns valid PyMOL commands for test inputs

---

### Task 3.3: Connect chat to LLM

**Location:** `modules/pymol/molecule_chat/chat_panel.py`

**Steps:**
1. In `ChatPanel.__init__`:
   - Initialize `self.llm_client = get_llm_client()`
2. In send message handler:
   - Get user input
   - Add user message to chat
   - Show "Thinking..." indicator
   - Call `translate_to_pymol()`
   - For each command: execute via PyMOL
   - Add bot response to chat
3. Add loading state (disable input while processing)
4. Handle errors gracefully (show in chat)

**Test criteria:** Full round-trip: user types → LLM translates → commands execute → response shown

---

## Phase 4: Command Execution & Screenshot

### Task 4.1: Implement PyMOL command execution

**Location:** `modules/pymol/molecule_chat/executor.py`

**Steps:**
1. Create `execute_command(pymol_cmd, cmd_object) -> tuple[str, bool]`:
   - Use `cmd_object.do()` or `cmd_object.extend()`
   - Capture output and errors
   - Return (result_message, success)
2. Create `execute_commands(commands: list[str], cmd_object) -> list[dict]`:
   - Execute each command in sequence
   - Collect results
   - Return list of {command, output, success}
3. Add error parsing for common PyMOL errors
4. Test: Various commands execute correctly

**Test criteria:** Commands run, errors captured, results returned

---

### Task 4.2: Add screenshot capture

**Location:** `modules/pymol/molecule_chat/screenshot.py`

**Steps:**
1. Create `capture_screenshot(cmd_object, path: str = None) -> bytes`:
   - Use `cmd_object.png()` to render to file
   - Support `dpi` and `ray` (ray-tracing) options
   - Return bytes
2. Create `get_temp_path(suffix: str) -> str` helper
3. Add configuration for screenshot quality (dpi)
4. Test: Screenshots capture current view

**Test criteria:** PNG files created, correct viewport rendered

---

### Task 4.3: Connect screenshot to chat flow

**Location:** `modules/pymol/molecule_chat/chat_panel.py`

**Steps:**
1. After command execution, call screenshot capture
2. Add screenshot to chat with `add_screenshot()`
3. Add "View updated" message
4. Test: Full flow with screenshot

**Test criteria:** Screenshot appears after commands

---

## Phase 5: Polish & Edge Cases

### Task 5.1: Add conversation history context

**Location:** `modules/pymol/molecule_chat/session.py`

**Steps:**
1. Create `ChatSession` class:
   - Track loaded objects (`cmd.get_names()`)
   - Track command history
   - Track view state
2. Update state after each command
3. Include context in LLM prompt
4. Test: Context improves command understanding

---

### Task 5.2: Error handling & recovery

**Steps:**
1. Catch PyMOL command errors → show in chat
2. Catch LLM API errors → retry logic, show status
3. Handle missing API key → show setup instructions
4. Validate commands before execution (optional)
5. Test various error scenarios

---

### Task 5.3: Voice input (optional enhancement)

**Location:** `modules/pymol/molecule_chat/voice.py`

**Steps:**
1. Add microphone button to chat panel
2. Use `whisper` CLI for transcription
3. Send transcribed text to chat
4. Test: Voice input works

---

## Phase 6: Testing & Documentation

### Task 6.1: Write unit tests

**Steps:**
1. Test command translator with known inputs
2. Test LLM client (mock if needed)
3. Test screenshot capture
4. Test configuration

---

### Task 6.2: Document usage

**Steps:**
1. Add docstrings to all classes/functions
2. Create help text in chat panel ("Type /help for commands")
3. Document API key setup process

---

## Task Dependencies

```
Phase 1 (Setup)
├── 1.1 Plugin scaffold ─────────▶ 1.2 Config system
└─────────────────────────────────▶ Phase 2

Phase 2 (UI)
├── 2.1 ChatPanel widget ───────▶ 2.3 Screenshot display
├── 2.2 Integrate into PyMOL ───┘
└─────────────────────────────────▶ Phase 3

Phase 3 (LLM)
├── 3.1 LLM client ─────────────▶ 3.3 Connect to chat
├── 3.2 Command translator ──────┘
└─────────────────────────────────▶ Phase 4

Phase 4 (Execution)
├── 4.1 Command executor ───────▶ 4.3 Connect to chat
├── 4.2 Screenshot capture ──────┘
└─────────────────────────────────▶ Phase 5

Phase 5 (Polish)
├── 5.1 Session context
├── 5.2 Error handling
└── 5.3 Voice (optional)

Phase 6
└── 6.1 Tests
└── 6.2 Docs
```

---

## Quick Reference for Agents

### Starting the plugin in development
```bash
cd /path/to/pymol-a
python -m pymol
# Or: pymol -R
```

### Finding the main GUI object
```python
from pymol import plugins
app = plugins.get_pmgapp()  # QApplication
# Main window usually: app.activeWindow() or similar
```

### Accessing PyMOL commands
```python
from pymol import cmd
cmd.show("cartoon", "all")
cmd.color("red", "chain A")
```

### Adding to Qt layouts
```python
layout = QtWidgets.QVBoxLayout()
parent.setLayout(layout)
layout.addWidget(widget)
```

---

*Created: 2026-02-20*
*For: Josh & Kep*
