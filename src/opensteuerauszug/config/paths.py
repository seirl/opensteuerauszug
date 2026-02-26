import os
from pathlib import Path
from typing import List

PROJECT_NAME = "opensteuerauszug"

def get_xdg_data_home() -> Path:
    """
    Returns the XDG data home directory for the project.
    Defaults to ~/.local/share/opensteuerauszug if XDG_DATA_HOME is not set.
    """
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / PROJECT_NAME
    return Path.home() / ".local" / "share" / PROJECT_NAME

def get_xdg_config_home() -> Path:
    """
    Returns the XDG config home directory for the project.
    Defaults to ~/.config/opensteuerauszug if XDG_CONFIG_HOME is not set.
    """
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / PROJECT_NAME
    return Path.home() / ".config" / PROJECT_NAME

def get_kursliste_search_paths() -> List[Path]:
    """
    Returns a list of paths to search for Kursliste files.
    Priority:
    1. XDG Data Home (e.g., ~/.local/share/opensteuerauszug/kursliste)
    2. Local Data Directory (e.g., ./data/kursliste)
    """
    paths = [
        get_xdg_data_home() / "kursliste",
        Path.cwd() / "data" / "kursliste",
    ]
    return paths

def get_config_search_paths() -> List[Path]:
    """
    Returns a list of paths to search for the configuration file.
    Priority:
    1. XDG Config Home (e.g., ~/.config/opensteuerauszug/config.toml)
    2. Local Config File (e.g., ./config.toml)
    """
    paths = [
        get_xdg_config_home() / "config.toml",
        Path.cwd() / "config.toml",
    ]
    return paths

def get_identifiers_search_paths() -> List[Path]:
    """
    Returns a list of paths to search for the security identifiers CSV file.
    Priority:
    1. XDG Config Home (e.g., ~/.config/opensteuerauszug/security_identifiers.csv)
    2. Local Data Directory (e.g., ./data/security_identifiers.csv)
    """
    paths = [
        get_xdg_config_home() / "security_identifiers.csv",
        Path.cwd() / "data" / "security_identifiers.csv",
    ]
    return paths
