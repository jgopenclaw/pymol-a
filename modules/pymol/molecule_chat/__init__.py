'''
MoleculeChat Plugin

A PyMOL plugin for molecular visualization and chat interaction.
'''

from . import chat_panel
from . import command_translator
from . import executor
from . import screenshot
from . import llm_client
from . import config

__all__ = ['chat_panel', 'command_translator', 'executor', 'screenshot', 'llm_client', 'config']

__plugin_name__ = 'MoleculeChat'
__plugin_author__ = 'MoleculeChat Team'
__plugin_version__ = '0.1.0'
__plugin_date__ = '2026-02-20'
__plugin_copyright__ = 'Copyright (C) 2026'
__plugin_license__ = 'MIT'
__plugin_url__ = 'https://github.com/moleculechat/molecule_chat'

def __plugin_activate__():
    print(' MoleculeChat plugin activated')
    return True


def __plugin_deactivate__():
    print(' MoleculeChat plugin deactivated')
    return True


def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt as addmenuitem
    addmenuitem('MoleculeChat', dialog)


def dialog():
    print(' MoleculeChat dialog opened')
    from pymol import cmd as _self
    from pymol.Qt import QtWidgets
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle('MoleculeChat')
    layout = QtWidgets.QVBoxLayout()
    label = QtWidgets.QLabel('MoleculeChat Plugin')
    layout.addWidget(label)
    dialog.setLayout(layout)
    dialog.show()
