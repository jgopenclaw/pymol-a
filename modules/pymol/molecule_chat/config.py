import json
import os

CONFIG_PATH = os.path.expanduser('~/.pymol/molecule_chat_config.json')

DEFAULT_CONFIG = {
    'provider': 'openai',
    'api_keys': {
        'openai': '',
        'anthropic': '',
        'ollama': ''
    },
    'model': 'gpt-4o',
    'ollama_base_url': 'http://localhost:11434',
    'screenshot_dpi': 150,
    'setup_complete': False
}


def save_config(config: dict) -> None:
    config_dir = os.path.dirname(CONFIG_PATH)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def get_api_key(provider: str) -> str:
    config = load_config()
    return config.get('api_keys', {}).get(provider, '')


def get_provider() -> str:
    config = load_config()
    return config.get('provider', 'openai')


def get_model() -> str:
    config = load_config()
    return config.get('model', 'gpt-4o')


def get_ollama_base_url() -> str:
    config = load_config()
    return config.get('ollama_base_url', 'http://localhost:11434')


def is_setup_complete() -> bool:
    config = load_config()
    return config.get('setup_complete', False)


def prompt_api_key_setup():
    from pymol.Qt import QtWidgets
    from pymol import cmd as _self

    config = load_config()
    
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle('MoleculeChat API Key Setup')
    dialog.setMinimumWidth(400)
    layout = QtWidgets.QVBoxLayout()

    provider_label = QtWidgets.QLabel('Select Provider:')
    layout.addWidget(provider_label)
    
    provider_combo = QtWidgets.QComboBox()
    provider_combo.addItems(['openai', 'anthropic', 'ollama'])
    provider_combo.setCurrentText(config.get('provider', 'openai'))
    layout.addWidget(provider_combo)

    api_key_label = QtWidgets.QLabel('API Key:')
    layout.addWidget(api_key_label)
    
    api_key_input = QtWidgets.QLineEdit()
    api_key_input.setPlaceholderText('Enter your API key')
    api_key_input.setText(config.get('api_keys', {}).get(provider_combo.currentText(), ''))
    api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
    layout.addWidget(api_key_input)

    model_label = QtWidgets.QLabel('Model (for OpenAI):')
    layout.addWidget(model_label)
    
    model_input = QtWidgets.QLineEdit()
    model_input.setPlaceholderText('gpt-4o')
    model_input.setText(config.get('model', 'gpt-4o'))
    layout.addWidget(model_input)

    def on_provider_changed():
        api_key_input.setText(config.get('api_keys', {}).get(provider_combo.currentText(), ''))
    
    provider_combo.currentTextChanged.connect(on_provider_changed)

    button_layout = QtWidgets.QHBoxLayout()
    
    cancel_button = QtWidgets.QPushButton('Cancel')
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_button)
    
    save_button = QtWidgets.QPushButton('Save')
    
    def save_settings():
        nonlocal config
        provider = provider_combo.currentText()
        api_key = api_key_input.text().strip()
        model = model_input.text().strip()
        
        if 'api_keys' not in config:
            config['api_keys'] = {}
        
        config['provider'] = provider
        config['api_keys'][provider] = api_key
        config['model'] = model if model else 'gpt-4o'
        config['setup_complete'] = bool(api_key)
        
        save_config(config)
        dialog.accept()
    
    save_button.clicked.connect(save_settings)
    button_layout.addWidget(save_button)
    
    layout.addLayout(button_layout)
    dialog.setLayout(layout)
    
    dialog.exec_()


def ensure_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
    return load_config()
