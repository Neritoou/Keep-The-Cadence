import sys
from pathlib import Path

# Función para obtener la ruta base del proyecto dependiendo si es un ejecutable o desarrollo
def get_base_path() -> Path:
    base_path = getattr(sys, "_MEIPASS", None)
    if base_path:
        return Path(base_path)
    
    # game/src/util/paths.py ->  game/
    return Path(__file__).resolve().parents[2]

# Ruta base del proyecto
BASE_PATH = get_base_path()

# Ruta a los assets
ASSETS_ROOT = BASE_PATH / "assets"

def get_asset(*paths: str) -> Path:
    """
    Devuelve la ruta absoluta de un asset como un objeto Path.

    Si una API requiere un string (por ejemplo, pygame), 
    se puede convertir usando str(path).

    Returns:
        Path: Ruta absoluta al asset solicitado.
    """
    path = ASSETS_ROOT.joinpath(*paths)

    if not path.is_file():
        raise FileNotFoundError(f"Paths: Asset {paths[-1]} no encontrado o inválido en la Ruta:\n{path}")
    return path

# --- SONGS ----
SONGS_ROOT = ASSETS_ROOT / "songs"

# --- Funciones para canciones ---
def list_song_folders() -> list[str]:
    """Lista los nombres de todas las subcarpetas dentro de assets/songs"""
    if not SONGS_ROOT.exists():
        return []
    return [p.name for p in SONGS_ROOT.iterdir() if p.is_dir()]

def _get_folder_path(folder_name: str) -> Path:
    """Devuelve el Path absoluto de una carpeta de canción por nombre"""
    path = SONGS_ROOT / folder_name
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Carpeta de canción '{folder_name}' no encontrada en {SONGS_ROOT}")
    return path

def get_full_song_path(folder_name: str) -> Path:
    path = _get_folder_path(folder_name) / "full_song.mpeg"
    if not path.is_file():
        raise FileNotFoundError(f"Paths: Full Song en el folder {folder_name} no encontrado o inválido en la Ruta:\n{path}")
    return path 

def get_voices_path(folder_name: str) -> Path:
    path = _get_folder_path(folder_name) / "voices.mp3"
    if not path.is_file():
        raise FileNotFoundError(f"Paths: Voices en el folder {folder_name} no encontrado o inválido en la Ruta:\n{path}")
    return path 

def get_inst_path(folder_name: str) -> Path:
    path = _get_folder_path(folder_name) / "inst.mp3"
    if not path.is_file():
        raise FileNotFoundError(f"Paths: Instrumental en el folder {folder_name} no encontrado o inválido en la Ruta:\n{path}")
    return path 

def get_chart_path(folder_name: str) -> Path:
    path = _get_folder_path(folder_name) / "chart.json"
    if not path.is_file():
        raise FileNotFoundError(f"Paths: Chart en el folder {folder_name} no encontrado o inválido en la Ruta:\n{path}")
    return path 