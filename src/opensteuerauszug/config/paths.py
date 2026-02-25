from pathlib import Path
import os
import sys

def get_xdg_data_home() -> Path:
    """Returns the XDG_DATA_HOME path."""
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

def get_xdg_config_home() -> Path:
    """Returns the XDG_CONFIG_HOME path."""
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

def resolve_security_identifiers_path(user_provided_path: str = None) -> Path:
    """
    Resolves the path to the security identifiers CSV file.
    Prioritizes user provided path, then XDG_CONFIG_HOME, then local 'data/security_identifiers.csv'.
    """
    if user_provided_path:
        return Path(user_provided_path)

    # 1. XDG Config
    xdg_config_path = get_xdg_config_home() / "opensteuerauszug" / "security_identifiers.csv"
    if xdg_config_path.exists():
        return xdg_config_path

    # 2. Local fallback (CWD)
    # Existing behavior was defaulting to project_root/data/security_identifiers.csv
    # When packaging, we assume running from a directory that might have a data folder
    return Path("data/security_identifiers.csv")

def resolve_kursliste_dirs(user_provided_dir: Path = None) -> list[Path]:
    """
    Resolves the directories to search for Kursliste files.
    If user_provided_dir is given, only that directory is returned.
    Otherwise, returns a list of existing default directories in priority order:
    1. XDG Data (for XML and SQLite)
    2. CWD data/kursliste
    """
    if user_provided_dir:
        # Return provided directory even if it doesn't exist, to let caller handle error
        return [user_provided_dir]

    dirs = []

    # 1. XDG Data (XML & SQLite)
    xdg_data_kursliste = get_xdg_data_home() / "opensteuerauszug" / "kursliste"
    if xdg_data_kursliste.exists():
        dirs.append(xdg_data_kursliste)

    # 2. Local fallback (cwd/data/kursliste, matching existing default behavior)
    cwd_kursliste = Path("data/kursliste")
    if cwd_kursliste.exists():
        dirs.append(cwd_kursliste)

    return dirs

def resolve_config_file(user_provided_path: Path = None) -> Path:
    """
    Resolves the configuration file path.
    Prioritizes user provided path, then XDG_CONFIG_HOME config.toml, then CWD config.toml.
    Defaults to 'config.toml' in CWD if nothing found.
    """
    if user_provided_path:
        return user_provided_path

    # 1. XDG Config
    xdg_config = get_xdg_config_home() / "opensteuerauszug" / "config.toml"
    if xdg_config.exists():
        return xdg_config

    # 2. CWD config.toml (Existing default behavior)
    cwd_config = Path("config.toml")
    if cwd_config.exists():
        return cwd_config

    # 3. Default (for error handling in ConfigManager)
    return cwd_config
