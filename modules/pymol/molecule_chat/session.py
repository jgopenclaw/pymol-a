from typing import List, Dict, Any, Optional


class ChatSession:
    """
    Manages state for a MoleculeChat session.
    
    Tracks loaded objects, command history, and view state
    for context-aware LLM interactions.
    """
    
    def __init__(self):
        self.objects: List[str] = []
        self.object_atom_counts: Dict[str, int] = {}
        self.command_history: List[Dict[str, Any]] = []
        self.view_state: Optional[List[float]] = None
        self.max_history: int = 50
    
    def update_from_pymol(self, cmd) -> None:
        """
        Refresh state from PyMOL.
        
        Args:
            cmd: PyMOL command object
        """
        self._update_objects(cmd)
        self._update_view_state(cmd)
    
    def _update_objects(self, cmd) -> None:
        """Update loaded objects from PyMOL."""
        try:
            names = cmd.get_names()
            if names and names[0]:
                self.objects = list(names[0])
            else:
                self.objects = []
        except Exception:
            self.objects = []
        
        self.object_atom_counts = {}
        try:
            all_obj = cmd.get_object_list()
            for obj in all_obj:
                try:
                    count = cmd.count_atoms(obj)
                    self.object_atom_counts[obj] = count
                except Exception:
                    self.object_atom_counts[obj] = 0
        except Exception:
            pass
    
    def _update_view_state(self, cmd) -> None:
        """Update view state from PyMOL."""
        try:
            self.view_state = list(cmd.get_view())
        except Exception:
            self.view_state = None
    
    def add_command(self, command: str, success: bool = True, output: str = "") -> None:
        """
        Add a command to history.
        
        Args:
            command: The executed command
            success: Whether the command succeeded
            output: Command output or error message
        """
        self.command_history.append({
            "command": command,
            "success": success,
            "output": output
        })
        
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]
    
    def get_context_prompt(self) -> str:
        """
        Format current state as context prompt for LLM.
        
        Returns:
            Formatted context string describing current state
        """
        lines = []
        
        if self.objects:
            lines.append("Loaded objects:")
            for obj in self.objects:
                count = self.object_atom_counts.get(obj, 0)
                if count > 0:
                    lines.append(f"  - {obj}: {count} atoms")
                else:
                    lines.append(f"  - {obj}")
        
        if self.command_history:
            recent = self.command_history[-5:]
            lines.append("\nRecent commands:")
            for entry in recent:
                status = "✓" if entry["success"] else "✗"
                lines.append(f"  {status} {entry['command']}")
        
        return "\n".join(lines) if lines else "No objects loaded"
    
    def get_recent_commands(self, count: int = 10) -> List[str]:
        """
        Get recent command strings.
        
        Args:
            count: Number of recent commands to return
            
        Returns:
            List of recent command strings
        """
        return [entry["command"] for entry in self.command_history[-count:]]
    
    def clear_history(self) -> None:
        """Clear command history."""
        self.command_history = []
    
    def has_objects(self) -> bool:
        """Check if any objects are loaded."""
        return len(self.objects) > 0
