# MoleculeChat Implementation Plan — Docked Panel

## Overview

Integrate a **chat panel** directly into PyMOL as a docked widget. Users can type natural language commands, see responses, and view rendered screenshots — all without leaving PyMOL.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        PyMOL Main Window                        │
├────────────────────────────────────────────────────────────────┤
│  Menu Bar                                                      │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌────────────────────────────────┐   │
│  │                     │  │                                │   │
│  │   Chat Panel       │  │      3D Viewport               │   │
│  │   (QDockWidget)    │  │      (PyMOLGLWidget)          │   │
│  │                     │  │                                │   │
│  │  ┌───────────────┐ │  │                                │   │
│  │  │ Chat History  │ │  │                                │   │
│  │  │               │ │  │                                │   │
│  │  │               │ │  │                                │   │
│  │  │               │ │  │                                │   │
│  │  ├───────────────┤ │  │                                │   │
│  │  │ Input:        │ │  │                                │   │
│  │  │ [__________] ▶│ │  │                                │   │
│  │  └───────────────┘ │  │                                │   │
│  └─────────────────────┘  └────────────────────────────────┘   │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Command Line / Feedback                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Infrastructure (Foundation)

**1.1 Create plugin structure**
```
modules/pymol/molecule_chat/
├── __init__.py           # Plugin entry point
├── chat_panel.py         # Main QWidget for chat UI
├── llm_client.py         # LLM API adapter (OpenAI/Ollama)
├── command_translator.py # NL → PyMOL command
├── screenshot.py         # Capture & verify renders
└── config.py            # API key, preferences
```

**1.2 Plugin entry point**
```python
# __init__.py
def __plugin__initialize__(self):
    from pymol import plugins
    plugins.addmenuitemqt('MoleculeChat', show_chat_panel)

def show_chat_panel():
    from pymol import plugins
    from .chat_panel import ChatPanel
    app = plugins.get_pmgapp()
    # Get main window and add docked widget
```

**1.3 Register with PyMOL**
- Add to plugin menu (Plugins → MoleculeChat)
- Keyboard shortcut (e.g., Ctrl+M)

---

### Phase 2: Chat Panel UI

**2.1 ChatPanel QWidget**
```python
class ChatPanel(QtWidgets.QWidget):
    def __init__(self, parent=None, pymol_instance=None):
        # Layout:
        # - QVBoxLayout
        #   - QScrollArea (chat history - markdown/rich text)
        #   - QHBoxLayout
        #     - QLineEdit (input)
        #     - QPushButton (send)
        #     - QPushButton (mic - optional voice)
```

**2.2 Chat message rendering**
- User messages: right-aligned, distinct color
- Bot messages: left-aligned, different color
- Error messages: red/warning style
- Support basic markdown (bold, code blocks for commands)

**2.3 Screenshot display**
- After each command execution, show thumbnail
- Click to enlarge
- Auto-scroll to latest

---

### Phase 3: LLM Integration

**3.1 LLMClient abstract interface**
```python
class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        pass

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)

class OllamaClient(LLMClient):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
```

**3.2 System prompt for command translation**
```
You are MoleculeChat, a PyMOL assistant. The user will describe 
what they want to see in natural language. 

Your job:
1. Translate their request into PyMOL commands
2. Execute them via the PyMOL API
3. Report results

Rules:
- Output ONLY valid PyMOL commands, one per line
- Use proper selection syntax (chain A, resi 1-50, name CA, etc.)
- If ambiguous, ask for clarification
- For complex requests, break into multiple commands

Available PyMOL commands: show, hide, color, zoom, center, 
orient, select, distance, angle, dihedral, fetch, load, ...
```

**3.3 Command execution**
```python
def execute_command(self, cmd_str: str) -> tuple[str, bool]:
    """Execute PyMOL command, return (output, success)"""
    try:
        result = self.pymol.cmd.extend(cmd_str)  # or cmd.do()
        return result, True
    except Exception as e:
        return str(e), False
```

---

### Phase 4: Screenshot Feedback

**4.1 Capture screenshot**
```python
def capture_screenshot(self, path: str = None) -> bytes:
    import tempfile
    if path is None:
        fd, path = tempfile.mkstemp(suffix='.png')
    self.pymol.cmd.png(path, dpi=150, ray=1)
    with open(path, 'rb') as f:
        return f.read()
```

**4.2 Verification (optional, Phase 2)**
- Send screenshot to vision-capable LLM
- Confirm command worked as intended

---

### Phase 5: State & Context

**5.1 Session state**
```python
class ChatSession:
    def __init__(self):
        self.loaded_objects: list[str] = []
        self.command_history: list[dict] = []
        self.view_state: dict = {}
    
    def update_from_pymol(self):
        # Query PyMOL for current state
        self.loaded_objects = self.pymol.cmd.get_names('all')
```

**5.2 Context injection**
```python
def get_context_prompt(self) -> str:
    return f"""
Current PyMOL state:
- Loaded objects: {', '.join(self.loaded_objects) or 'none'}
- Current selection: {self.pymol.cmd.get('selection_names')}
- View: {self.pymol.cmd.get_view()}
"""
```

---

## Key Files to Modify

| File | Change |
|------|--------|
| `modules/pymol/__init__.py` | Add `molecule_chat` to startup path |
| `modules/pymol/molecule_chat/__init__.py` | Plugin entry point |
| `modules/pymol/molecule_chat/chat_panel.py` | Main UI widget |
| `modules/pmg_qt/pymol_qt_gui.py` | Add `open_chat_panel()` method, menu item |
| `data/startup/` | Could add startup plugin (optional) |

---

## Dependencies

```
# Required
pymol (this fork)
PyQt5 or PyQt6 (depending on PyMOL version)

# LLM (user provides API key or uses local)
openai        # OpenAI API
ollama        # Local LLM
anthropic     # Optional: Claude

# Optional
pyaudio       # Voice input
Pillow        # Screenshot processing
```

---

## Configuration

**API Key Storage**
- Store in `~/.pymol/molecule_chat_config.json`
- Or use PyMOL's built-in `cmd.set()` namespace

```python
# config.py
import os
import json

CONFIG_PATH = os.path.expanduser("~/.pymol/molecule_chat_config.json")

def get_api_key(provider: str) -> str:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            return config.get(f"{provider}_api_key")
    return None
```

---

## Menu Integration

**Suggested menu location:** Plugins → MoleculeChat

```python
# In pymol_qt_gui.py
def open_chat_panel(self):
    from pymol.molecule_chat import chat_panel
    if not self.chat_panel:
        self.chat_panel = chat_panel.ChatPanel(self, self.pymolwidget.pymol)
        self.addDockWidget(Qt.RightDockWidgetArea, self.chat_panel)
    self.chat_panel.show()
    self.chat_panel.raise_()
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+M / Cmd+M | Toggle chat panel |
| Enter | Send message |
| Shift+Enter | New line in input |
| Ctrl+L | Clear chat history |

---

## Error Handling

1. **Invalid commands:** Show error in chat, suggest corrections
2. **API failures:** Retry with backoff, show status
3. **No API key:** Prompt user with setup instructions
4. **PyMOL errors:** Parse and display nicely

---

## Future Enhancements (Post-MVP)

- [ ] Voice input (Whisper)
- [ ] Voice output (TTS)
- [ ] Screenshot verification loop
- [ ] Multi-structure context
- [ ] Biology-aware explanations
- [ ] Command suggestions / autocomplete
- [ ] Conversation export

---

## Acceptance Criteria

1. ✅ Chat panel appears as docked widget in PyMOL
2. ✅ User can type natural language commands
3. ✅ Commands are translated to PyMOL syntax and executed
4. ✅ Results are displayed in chat
5. ✅ Screenshots are captured and shown after commands
6. ✅ Works with user-provided OpenAI API key
7. ✅ Basic error handling for failed commands

---

*Plan created: 2026-02-20*
