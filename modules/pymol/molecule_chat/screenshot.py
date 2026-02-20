import os
import tempfile

from pymol.molecule_chat.config import load_config


def get_temp_path(suffix: str) -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


def capture_screenshot(cmd_object, path: str = None, dpi: int = None, ray: bool = False) -> bytes:
    if dpi is None:
        config = load_config()
        dpi = config.get('screenshot_dpi', 150)
    
    if path is None:
        path = get_temp_path('.png')
        cleanup_temp = True
    else:
        cleanup_temp = False
    
    try:
        cmd_object.png(path, dpi=float(dpi), ray=int(ray))
        
        with open(path, 'rb') as f:
            image_bytes = f.read()
        
        return image_bytes
    finally:
        if cleanup_temp and os.path.exists(path):
            os.remove(path)
