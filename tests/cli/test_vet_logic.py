import pytest
import uuid
from pathlib import Path
from ruamel.yaml import YAML

from flashcore.cli._vet_logic import vet_logic


@pytest.fixture
def yaml_handler():
    """Provides a configured ruamel.yaml instance."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def test_vet_logic_no_yaml_files(tmp_path: Path, capsys):
    """
    Tests that vet_logic handles directories with no YAML files gracefully.
    """
    # Create a non-yaml file to ensure it's ignored
    (tmp_path / "some_file.txt").write_text("hello")

    files = list(tmp_path.glob("*.yml"))
    changes_needed = vet_logic(files_to_process=files, check=False)

    captured = capsys.readouterr()
    assert not changes_needed
    assert "No YAML files found to vet." in captured.out


def test_vet_logic_clean_files_check_mode(tmp_path: Path, yaml_handler, capsys):
    """
    Tests that vet_logic in --check mode correctly identifies clean files.
    """
    # Keys must be sorted alphabetically for the file to be considered "clean"
    # Use a valid UUID format and sort card keys alphabetically (a, q, uuid)
    valid_uuid = str(uuid.uuid4())
    clean_content = {
        "cards": [{"a": "A1", "q": "Q1", "uuid": valid_uuid}],
        "deck": "Test Deck",
    }
    with (tmp_path / "clean.yml").open("w") as f:
        yaml_handler.dump(clean_content, f)

    files = list(tmp_path.glob("*.yml"))
    changes_needed = vet_logic(files_to_process=files, check=True)

    captured = capsys.readouterr()
    assert not changes_needed
    assert "All files are clean" in captured.out


def test_vet_logic_clean_files_modify_mode(tmp_path: Path, yaml_handler, capsys):
    """
    Tests that vet_logic in modify mode makes no changes to clean files.
    """
    # Keys must be sorted alphabetically for the file to be considered "clean"
    # Use a valid UUID format and sort card keys alphabetically (a, q, uuid)
    valid_uuid = str(uuid.uuid4())
    clean_content = {
        "cards": [{"a": "A1", "q": "Q1", "uuid": valid_uuid}],
        "deck": "Test Deck",
    }
    file_path = tmp_path / "clean.yml"
    with file_path.open("w") as f:
        yaml_handler.dump(clean_content, f)

    original_mtime = file_path.stat().st_mtime
    files = list(tmp_path.glob("*.yml"))
    changes_needed = vet_logic(files_to_process=files, check=False)
    new_mtime = file_path.stat().st_mtime

    captured = capsys.readouterr()
    assert not changes_needed
    assert "All files are clean" in captured.out
    assert original_mtime == new_mtime


def test_vet_logic_dirty_files_check_mode(tmp_path: Path, yaml_handler, capsys):
    """
    Tests that vet_logic in --check mode correctly identifies dirty files.
    """
    dirty_content = {
        "deck": "Test Deck",
        "cards": [{"q": "Q1", "a": "A1"}, {"uuid": "", "q": "Q2", "a": "A2"}],
    }
    with (tmp_path / "dirty.yml").open("w") as f:
        yaml_handler.dump(dirty_content, f)

    files = list(tmp_path.glob("*.yml"))
    changes_needed = vet_logic(files_to_process=files, check=True)

    captured = capsys.readouterr()
    assert changes_needed
    assert (
        "Check failed: Some files need changes. Run without --check to fix."
        in captured.out
    )


def test_vet_logic_dirty_files_modify_mode(tmp_path: Path, yaml_handler, capsys):
    """
    Tests that vet_logic in modify mode correctly adds UUIDs to dirty files.
    """
    dirty_content = {
        "deck": "Test Deck",
        "cards": [{"q": "Q1", "a": "A1"}, {"uuid": "", "q": "Q2", "a": "A2"}],
    }
    file_path = tmp_path / "dirty.yml"
    with file_path.open("w") as f:
        yaml_handler.dump(dirty_content, f)

    files = list(tmp_path.glob("*.yml"))
    changes_needed = vet_logic(files_to_process=files, check=False)

    captured = capsys.readouterr()
    assert changes_needed
    assert "File formatted successfully: dirty.yml" in captured.out

    with file_path.open("r") as f:
        data = yaml_handler.load(f)

    # Check that keys are sorted
    assert list(data.keys()) == ["cards", "deck"]
    assert "uuid" in data["cards"][0]
    assert data["cards"][0]["uuid"] is not None
    assert len(data["cards"][0]["uuid"]) > 1  # Check it's not empty
    assert "uuid" in data["cards"][1]
    assert data["cards"][1]["uuid"] is not None
    assert len(data["cards"][1]["uuid"]) > 1


def test_vet_logic_ignores_invalid_yaml_structure(tmp_path: Path):
    """
    Tests that vet_logic ignores YAML files with unexpected structures.
    """
    # This is a list at the root, not a dict with a 'cards' key
    invalid_content = "- card: 1\n- card: 2"
    file_path = tmp_path / "invalid.yml"
    file_path.write_text(invalid_content)

    original_mtime = file_path.stat().st_mtime
    files = list(tmp_path.glob("*.yml"))
    changes_needed = vet_logic(files_to_process=files, check=False)
    new_mtime = file_path.stat().st_mtime

    assert not changes_needed
    assert original_mtime == new_mtime
