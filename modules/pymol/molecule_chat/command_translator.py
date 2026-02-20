from typing import List
from .llm_client import get_llm_client, MissingAPIKeyError


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


def translate_to_pymol(user_input: str, context: str = "") -> List[str]:
    """
    Translate natural language user input into PyMOL commands.
    
    Args:
        user_input: The natural language input from the user
        context: Additional context about current state (objects, view, etc.)
    
    Returns:
        List of PyMOL commands to execute
    
    Raises:
        MissingAPIKeyError: If no API key is configured
    """
    llm_client = get_llm_client()
    
    full_context = context.strip() if context else ""
    context_section = ""
    if full_context:
        context_section = f"""
## Current State
{full_context}

"""
    
    full_prompt = f"{SYSTEM_PROMPT}\n{context_section}\nUser: \"{user_input}\"\nOutput:"
    
    messages = [
        {"role": "system", "content": "You are a PyMOL command translator. Output only PyMOL commands, one per line, with no explanations."},
        {"role": "user", "content": full_prompt}
    ]
    
    response = llm_client.chat(messages)
    
    commands = []
    for line in response.strip().split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            commands.append(line)
    
    return commands


def get_current_context(cmd) -> str:
    """
    Get current PyMOL context for injection into the translator.
    
    Args:
        cmd: PyMOL command object
    
    Returns:
        String describing current objects and view state
    """
    context_lines = []
    
    try:
        names = cmd.get_names()
        if names and names[0]:
            objects = names[0]
            if objects:
                context_lines.append(f"Loaded objects: {', '.join(objects)}")
    except Exception:
        pass
    
    try:
        all_obj = cmd.get_object_list()
        if all_obj:
            for obj in all_obj:
                try:
                    count = cmd.count_atoms(f"{obj}")
                    context_lines.append(f"  - {obj}: {count} atoms")
                except Exception:
                    context_lines.append(f"  - {obj}")
    except Exception:
        pass
    
    return "\n".join(context_lines)
