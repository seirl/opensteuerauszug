from pathlib import Path
import os
import sys

def get_xdg_data_home() -> Path:
    """Returns the XDG_DATA_HOME path."""
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

def get_xdg_cache_home() -> Path:
    """Returns the XDG_CACHE_HOME path."""
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))

def get_project_root() -> Path:
    """Returns the root directory of the project."""
    # Based on assumption that this file is in src/opensteuerauszug/config/paths.py
    current_file = Path(__file__)
    src_opensteuerauszug_config = current_file.parent
    src_opensteuerauszug = src_opensteuerauszug_config.parent
    src = src_opensteuerauszug.parent
    project_root = src.parent
    return project_root

def resolve_security_identifiers_path(user_provided_path: str = None) -> Path:
    """
    Resolves the path to the security identifiers CSV file.
    Prioritizes user provided path, then XDG_DATA_HOME, then local project data.
    """
    if user_provided_path:
        return Path(user_provided_path)

    # 1. XDG Data
    xdg_path = get_xdg_data_home() / "opensteuerauszug" / "security_identifiers.csv"
    if xdg_path.exists():
        return xdg_path

    # 2. Local fallback (Project Root)
    # Existing behavior was defaulting to project_root/data/security_identifiers.csv
    local_path = get_project_root() / "data" / "security_identifiers.csv"
    return local_path

def resolve_kursliste_dirs(user_provided_dir: Path = None) -> list[Path]:
    """
    Resolves the directories to search for Kursliste files.
    If user_provided_dir is given, only that directory is returned.
    Otherwise, returns a list of existing default directories in priority order:
    1. XDG Cache (for SQLite)
    2. XDG Data (for XML)
    3. CWD data/kursliste
    4. Project Root data/kursliste
    """
    if user_provided_dir:
        # Return provided directory even if it doesn't exist, to let caller handle error
        return [user_provided_dir]

    dirs = []

    # 1. XDG Cache (SQLite)
    xdg_cache_kursliste = get_xdg_cache_home() / "opensteuerauszug" / "kursliste"
    if xdg_cache_kursliste.exists():
        dirs.append(xdg_cache_kursliste)

    # 2. XDG Data (XML)
    xdg_data_kursliste = get_xdg_data_home() / "opensteuerauszug" / "kursliste"
    if xdg_data_kursliste.exists():
        dirs.append(xdg_data_kursliste)

    # 3. Local fallback (cwd/data/kursliste, matching existing default behavior)
    cwd_kursliste = Path("data/kursliste")
    if cwd_kursliste.exists():
        dirs.append(cwd_kursliste)

    # 4. Project Root fallback
    project_kursliste = get_project_root() / "data" / "kursliste"

    # Check if we should add project_kursliste
    if project_kursliste.exists():
        # Only add if it's different from cwd_kursliste (if cwd_kursliste exists)
        if not cwd_kursliste.exists() or project_kursliste.resolve() != cwd_kursliste.resolve():
            dirs.append(project_kursliste)

    return dirs
