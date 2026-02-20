from typing import List, Optional
from .llm_client import get_llm_client, MissingAPIKeyError
from .session import ChatSession


SYSTEM_PROMPT = """You are a PyMOL command translator. Your task is to convert natural language requests from users into valid PyMOL commands.

## Role
You are an expert PyMOL user who understands molecular visualization and can translate plain English commands into precise PyMOL commands.

## Rules
1. Only output valid PyMOL commands - one command per line
2. Use proper selection syntax (e.g., "chain A", "resi 1-50", "name CA")
3. Commands should be complete and executable
4. Do not include comments or explanations in the output
5. Each command should be on its own line
6. Use standard PyMOL command names (show, color, hide, zoom, center, etc.)

## Examples of Natural Language to PyMOL Command Mapping

Example 1:
User: "Show the protein as cartoon"
Output: show cartoon, all

Example 2:
User: "Color each chain differently"
Output: color red, chain A
color blue, chain B
color green, chain C
color yellow, chain D

Example 3:
User: "Zoom into the active site"
Output: zoom (resi 100-150)

Example 4:
User: "Center on residue 50"
Output: center resi 50

Example 5:
User: "Show only chain B as sticks"
Output: hide all
show sticks, chain B

Example 6:
User: "Color the structure by b-factor"
Output: spectrum b, rainbow

Example 7:
User: "Show hydrogen atoms"
Output: show sticks, hydro

Example 8:
User: "Hide everything except the ligand"
Output: hide all
show sticks, organic

Example 9:
User: "Make the background white"
Output: set bg_color, white

Example 10:
User: "Rotate the view 90 degrees"
Output: turn x, 90

Now translate the following user request into PyMOL commands:"""


def translate_to_pymol(user_input: str, session: Optional[ChatSession] = None) -> List[str]:
    """
    Translate natural language user input into PyMOL commands.
    
    Args:
        user_input: The natural language input from the user
        session: ChatSession for context
    
    Returns:
        List of PyMOL commands to execute
    
    Raises:
        MissingAPIKeyError: If no API key is configured
    """
    llm_client = get_llm_client()
    
    context = session.get_context_prompt() if session else ""
    
    if context:
        context_section = f"\n## Current State\n{context}\n"
    else:
        context_section = ""
    
    full_prompt = f"{SYSTEM_PROMPT}{context_section}\nUser: \"{user_input}\"\nOutput:"
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.strip()},
        {"role": "user", "content": full_prompt}
    ]
    
    response = llm_client.chat(messages)
    
    commands = [
        line.strip() for line in response.strip().split('\n')
        if line.strip() and not line.strip().startswith('#')
    ]
    
    return commands
