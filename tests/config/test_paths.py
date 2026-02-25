import os
import pytest
from pathlib import Path
from unittest.mock import patch
from opensteuerauszug.config import paths

@pytest.fixture
def xdg_env(tmp_path):
    # Setup XDG env vars pointing to temp dir
    data_home = tmp_path / "share"
    config_home = tmp_path / "config"
    data_home.mkdir()
    config_home.mkdir()

    env_vars = {
        "XDG_DATA_HOME": str(data_home),
        "XDG_CONFIG_HOME": str(config_home),
    }

    with patch.dict(os.environ, env_vars):
        yield data_home, config_home

def test_resolve_security_identifiers_path_user_provided():
    # User provided path always returned as Path
    path = paths.resolve_security_identifiers_path("/custom/path.csv")
    assert path == Path("/custom/path.csv")

def test_resolve_security_identifiers_path_xdg_config(xdg_env):
    _, config_home = xdg_env

    # Create file in XDG CONFIG home (primary)
    app_config = config_home / "opensteuerauszug"
    app_config.mkdir(parents=True)
    csv_file = app_config / "security_identifiers.csv"
    csv_file.touch()

    resolved = paths.resolve_security_identifiers_path()
    assert resolved == csv_file

def test_resolve_security_identifiers_path_fallback_local(xdg_env, tmp_path):
    # XDG files missing

    # Create file in CWD/data
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    data_dir = cwd_dir / "data"
    data_dir.mkdir()

    original_cwd = os.getcwd()
    os.chdir(cwd_dir)
    try:
        resolved = paths.resolve_security_identifiers_path()
        assert resolved == Path("data/security_identifiers.csv")
    finally:
        os.chdir(original_cwd)

def test_resolve_kursliste_dirs_user_provided(tmp_path):
    user_dir = tmp_path / "custom_kursliste"
    # Even if not exists, user provided is returned
    resolved = paths.resolve_kursliste_dirs(user_dir)
    assert resolved == [user_dir]

def test_resolve_kursliste_dirs_all_exist(xdg_env, tmp_path):
    data_home, _ = xdg_env

    # Create XDG Data dir (Now priority)
    data_kursliste = data_home / "opensteuerauszug" / "kursliste"
    data_kursliste.mkdir(parents=True)

    # Create CWD dir
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    (cwd_dir / "data" / "kursliste").mkdir(parents=True)

    original_cwd = os.getcwd()
    os.chdir(cwd_dir)
    try:
        resolved = paths.resolve_kursliste_dirs()

        # Expected order: XDG Data -> CWD
        assert len(resolved) == 2
        assert resolved[0] == data_kursliste
        assert resolved[1] == Path("data/kursliste")
    finally:
        os.chdir(original_cwd)

def test_resolve_config_file_user_provided():
    path = paths.resolve_config_file(Path("/custom/config.toml"))
    assert path == Path("/custom/config.toml")

def test_resolve_config_file_cwd_exists(xdg_env, tmp_path):
    # If both exist, XDG should win now based on new requirement
    _, config_home = xdg_env

    # Create XDG config
    app_config = config_home / "opensteuerauszug"
    app_config.mkdir(parents=True)
    xdg_file = app_config / "config.toml"
    xdg_file.touch()

    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    config_file = cwd_dir / "config.toml"
    config_file.touch()

    original_cwd = os.getcwd()
    os.chdir(cwd_dir)
    try:
        resolved = paths.resolve_config_file()
        assert resolved == xdg_file
    finally:
        os.chdir(original_cwd)

def test_resolve_config_file_cwd_fallback(xdg_env, tmp_path):
    # Only CWD exists
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    config_file = cwd_dir / "config.toml"
    config_file.touch()

    original_cwd = os.getcwd()
    os.chdir(cwd_dir)
    try:
        resolved = paths.resolve_config_file()
        # The function returns Path("config.toml") which is relative to CWD
        # The test constructed an absolute path fixture. We need to compare properly.
        assert resolved.resolve() == config_file.resolve()
    finally:
        os.chdir(original_cwd)

def test_resolve_config_file_default(xdg_env, tmp_path):
    # Neither exists, return default relative path
    cwd_dir = tmp_path / "clean_cwd"
    cwd_dir.mkdir()

    original_cwd = os.getcwd()
    os.chdir(cwd_dir)
    try:
        resolved = paths.resolve_config_file()
        assert resolved == Path("config.toml")
    finally:
        os.chdir(original_cwd)
