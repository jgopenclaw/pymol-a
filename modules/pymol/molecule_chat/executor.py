import re
import io
import sys
from typing import List, Tuple, Dict


ERROR_PATTERNS = {
    "selection": re.compile(r"(?i)(selection|selector).*?not found|unknown (selection|object)"),
    "object": re.compile(r"(?i)object .*? not found|unknown object"),
    "command": re.compile(r"(?i)unknown command|invalid command|syntax error"),
    "file": re.compile(r"(?i)(file|directory).*?not found|cannot open"),
    "argument": re.compile(r"(?i)invalid argument|wrong number of arguments|missing required argument"),
}


def parse_error(error_message: str) -> str:
    """
    Parse PyMOL error message into human-readable format.
    
    Args:
        error_message: Raw error message from PyMOL
    
    Returns:
        Human-readable error description
    """
    error_message = error_message.strip()
    
    if not error_message:
        return "Unknown error occurred"
    
    for error_type, pattern in ERROR_PATTERNS.items():
        if pattern.search(error_message):
            if error_type == "selection":
                return f"Selection error: {error_message}"
            elif error_type == "object":
                return f"Object error: {error_message}"
            elif error_type == "command":
                return f"Command error: {error_message}"
            elif error_type == "file":
                return f"File error: {error_message}"
            elif error_type == "argument":
                return f"Argument error: {error_message}"
    
    return f"Error: {error_message}"


def execute_command(pymol_cmd: str, cmd_object) -> Tuple[str, bool]:
    """
    Execute a single PyMOL command.
    
    Args:
        pymol_cmd: The PyMOL command string to execute
        cmd_object: The PyMOL command object (usually cmd module)
    
    Returns:
        Tuple of (result_message, success)
    """
    if not pymol_cmd or not pymol_cmd.strip():
        return ("Empty command skipped", True)
    
    pymol_cmd = pymol_cmd.strip()
    
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        cmd_object.do(pymol_cmd)
        
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        if stderr_output:
            error_msg = parse_error(stderr_output)
            return (error_msg, False)
        
        if stdout_output:
            return (stdout_output.strip(), True)
        
        return (f"Executed: {pymol_cmd}", True)
        
    except Exception as e:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        error_msg = parse_error(str(e))
        return (error_msg, False)
    
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def execute_commands(commands: List[str], cmd_object) -> List[Dict]:
    """
    Execute a list of PyMOL commands in sequence.
    
    Args:
        commands: List of PyMOL command strings to execute
        cmd_object: The PyMOL command object (usually cmd module)
    
    Returns:
        List of dictionaries, each containing:
        - command: The original command string
        - output: The result or error message
        - success: Boolean indicating if command succeeded
    """
    results = []
    
    for cmd in commands:
        if not cmd or not cmd.strip():
            continue
        
        output, success = execute_command(cmd, cmd_object)
        
        results.append({
            "command": cmd,
            "output": output,
            "success": success
        })
    
    return results
