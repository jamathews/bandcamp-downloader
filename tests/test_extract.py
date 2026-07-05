import os
import sys
import json
import pytest
from extract import Mapper, get_dest
from unittest.mock import MagicMock, patch

def test_mapper_init(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    output_dir = tmp_path / "output"
    mapper = Mapper(str(mapping_file), str(output_dir))
    assert mapper._mapping_file == str(mapping_file)
    assert mapper._output_dir == str(output_dir)

def test_mapper_load_save(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    output_dir = tmp_path / "output"
    mapper = Mapper(str(mapping_file), str(output_dir))
    
    # Test initial load (creates file)
    assert mapper.mapping == {}
    assert mapping_file.exists()
    
    # Test add and save
    mapper.add("Artist", "Folder")
    assert mapper.mapping["Artist"] == "Folder"
    
    with open(mapping_file) as f:
        data = json.load(f)
        assert data["Artist"] == "Folder"

def test_mapper_get_artist_root_folder_existing(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    with open(mapping_file, "w") as f:
        json.dump({"Artist": "ExistingFolder"}, f)
    
    mapper = Mapper(str(mapping_file), str(tmp_path))
    assert mapper.get_artist_root_folder("Artist") == "ExistingFolder"

def test_get_dest():
    mapper = MagicMock()
    mapper.get_artist_root_folder.return_value = "RootFolder"
    
    # Use os.path.join to ensure cross-platform compatibility in test expectations
    archive = os.path.join("path", "to", "zips", "Artist Name", "Album Name.zip")
    output_dir = "output"
    subfolder = "Sub"
    
    dest = get_dest(archive, mapper, output_dir, subfolder)
    
    expected = os.path.join("output", "RootFolder", "Artist Name", "Album Name", "Sub")
    assert dest == expected

def test_mapper_get_folder_input(tmp_path):
    mapper = Mapper(str(tmp_path / "map.json"), str(tmp_path))
    with patch('builtins.input', return_value="ManualFolder"):
        folder = mapper._get_folder("Artist")
        assert str(folder) == "ManualFolder"

def test_mapper_get_folder_existing_dir(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    artist_dir = output_dir / "ExistingRoot" / "Artist"
    artist_dir.mkdir(parents=True)
    
    mapper = Mapper(str(tmp_path / "map.json"), str(output_dir))
    # It should find "ExistingRoot"
    folder = mapper._get_folder("Artist")
    assert folder == "ExistingRoot"
