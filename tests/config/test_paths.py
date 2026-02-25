import os
import pytest
from pathlib import Path
from unittest.mock import patch
from opensteuerauszug.config import paths

@pytest.fixture
def xdg_env(tmp_path):
    # Setup XDG env vars pointing to temp dir
    data_home = tmp_path / "share"
    cache_home = tmp_path / "cache"
    data_home.mkdir()
    cache_home.mkdir()

    env_vars = {
        "XDG_DATA_HOME": str(data_home),
        "XDG_CACHE_HOME": str(cache_home),
    }

    with patch.dict(os.environ, env_vars):
        yield data_home, cache_home

@pytest.fixture
def mock_project_root(tmp_path):
    project_root = tmp_path / "project_root"
    project_root.mkdir()
    with patch("opensteuerauszug.config.paths.get_project_root", return_value=project_root):
        yield project_root

def test_resolve_security_identifiers_path_user_provided():
    # User provided path always returned as Path
    path = paths.resolve_security_identifiers_path("/custom/path.csv")
    assert path == Path("/custom/path.csv")

def test_resolve_security_identifiers_path_xdg(xdg_env):
    data_home, _ = xdg_env

    # Create file in XDG data home
    app_data = data_home / "opensteuerauszug"
    app_data.mkdir(parents=True)
    csv_file = app_data / "security_identifiers.csv"
    csv_file.touch()

    resolved = paths.resolve_security_identifiers_path()
    assert resolved == csv_file

def test_resolve_security_identifiers_path_fallback_local(xdg_env, mock_project_root):
    # XDG file missing

    # Create file in project data dir
    data_dir = mock_project_root / "data"
    data_dir.mkdir()
    csv_file = data_dir / "security_identifiers.csv"
    csv_file.touch()

    resolved = paths.resolve_security_identifiers_path()
    assert resolved == csv_file

def test_resolve_security_identifiers_path_none_exists(xdg_env, mock_project_root):
    # Neither exists
    # Should return local fallback path
    expected = mock_project_root / "data" / "security_identifiers.csv"
    resolved = paths.resolve_security_identifiers_path()
    assert resolved == expected

def test_resolve_kursliste_dirs_user_provided(tmp_path):
    user_dir = tmp_path / "custom_kursliste"
    # Even if not exists, user provided is returned
    resolved = paths.resolve_kursliste_dirs(user_dir)
    assert resolved == [user_dir]

def test_resolve_kursliste_dirs_all_exist(xdg_env, mock_project_root):
    data_home, cache_home = xdg_env

    # Create XDG Cache dir
    cache_kursliste = cache_home / "opensteuerauszug" / "kursliste"
    cache_kursliste.mkdir(parents=True)

    # Create XDG Data dir
    data_kursliste = data_home / "opensteuerauszug" / "kursliste"
    data_kursliste.mkdir(parents=True)

    # Create Project Root dir
    project_kursliste = mock_project_root / "data" / "kursliste"
    project_kursliste.mkdir(parents=True)

    # Create CWD dir
    cwd_dir = mock_project_root / "cwd" # Separate from project root to test distinction
    cwd_dir.mkdir()
    (cwd_dir / "data" / "kursliste").mkdir(parents=True)

    original_cwd = os.getcwd()
    os.chdir(cwd_dir)
    try:
        resolved = paths.resolve_kursliste_dirs()

        assert len(resolved) == 4
        assert resolved[0] == cache_kursliste
        assert resolved[1] == data_kursliste
        assert resolved[2] == Path("data/kursliste")
        # resolved[2] is relative, so check resolve() matches
        assert resolved[2].resolve() == (cwd_dir / "data" / "kursliste").resolve()
        assert resolved[3] == project_kursliste
    finally:
        os.chdir(original_cwd)

def test_resolve_kursliste_dirs_only_project_root(xdg_env, mock_project_root):
    # Only project root exists
    project_kursliste = mock_project_root / "data" / "kursliste"
    project_kursliste.mkdir(parents=True)

    # Ensure CWD data/kursliste does not exist
    cwd_dir = mock_project_root / "clean_cwd"
    cwd_dir.mkdir()

    original_cwd = os.getcwd()
    os.chdir(cwd_dir)
    try:
        resolved = paths.resolve_kursliste_dirs()
        assert len(resolved) == 1
        assert resolved[0] == project_kursliste
    finally:
        os.chdir(original_cwd)

def test_resolve_kursliste_dirs_deduplication(xdg_env, mock_project_root):
    # If CWD is project root, data/kursliste exists in both concepts but refers to same directory.

    project_kursliste = mock_project_root / "data" / "kursliste"
    project_kursliste.mkdir(parents=True)

    original_cwd = os.getcwd()
    os.chdir(mock_project_root)
    try:
        resolved = paths.resolve_kursliste_dirs()
        # Should contain CWD path, but NOT project root path (deduplicated)
        # Because logic checks: if project_kursliste.resolve() != cwd_kursliste.resolve(): append

        # In this case cwd_kursliste exists (it's "data/kursliste" relative to CWD=project_root).
        # And resolve() will be equal.

        # So resolved list should have only 1 entry (assuming XDG don't exist)
        assert len(resolved) == 1
        assert resolved[0] == Path("data/kursliste")
    finally:
        os.chdir(original_cwd)
