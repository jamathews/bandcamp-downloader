import importlib.util
import os
import sys
import datetime
import pytest
from unittest.mock import MagicMock

# Import the script
script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bandcamp-downloader.py'))
spec = importlib.util.spec_from_file_location("bandcamp_downloader", script_path)
bd = importlib.util.module_from_spec(spec)
sys.modules["bandcamp_downloader"] = bd
# Mock TQDM before exec_module if it's used at module level
# It is used in CONFIG but not immediately.
spec.loader.exec_module(bd)

def test_sanitize_filename():
    if sys.platform.startswith('win'):
        assert bd.sanitize_filename('test/file:*.mp3') == 'test-file--.mp3'
    else:
        assert bd.sanitize_filename("test/file.mp3") == "test-file.mp3"

def test_sanitize_filename_windows(monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'win32')
    # Re-evaluating the regex or how the function behaves might be needed if it was already defined
    # The function uses sys.platform.startswith('win') inside it.
    assert bd.sanitize_filename('test/file:*.mp3') == 'test-file--.mp3'

def test_purchase_time_ok():
    cutoff = datetime.datetime(2023, 1, 1)
    item_new = {'purchased': '01 Jan 2024 12:00:00 GMT'}
    item_old = {'purchased': '01 Jan 2022 12:00:00 GMT'}
    item_missing = {}
    
    assert bd.purchase_time_ok(item_new, cutoff) is True
    assert bd.purchase_time_ok(item_old, cutoff) is False
    assert bd.purchase_time_ok(item_missing, cutoff) is True

def test_key_for_item():
    item = {'sale_item_type': 'a', 'sale_item_id': 123}
    assert bd.key_for_item(item) == 'a123'

def test_item_has_key():
    assert bd.item_has_key({'sale_item_type': 'a', 'sale_item_id': 123}) is True
    assert bd.item_has_key({'sale_item_type': 'a'}) is False
    assert bd.item_has_key({}) is False

def test_extension_from_url():
    assert bd.extension_from_url("https://example.com/file.mp3?token=123") == ".mp3"
    assert bd.extension_from_url("https://example.com/file") == ""

def test_extension_from_type():
    original_format = bd.CONFIG['FORMAT']
    try:
        bd.CONFIG['FORMAT'] = 'mp3-320'
        assert bd.extension_from_type('a', 'mp3-320') == '.zip'
        assert bd.extension_from_type('t', 'mp3-320') == '.mp3'
        
        bd.CONFIG['FORMAT'] = 'flac'
        assert bd.extension_from_type('t', 'flac') == '.flac'
        
        bd.CONFIG['FORMAT'] = 'nonexistent'
        assert bd.extension_from_type('t', 'nonexistent') == ''
    finally:
        bd.CONFIG['FORMAT'] = original_format

def test_merge_items_and_urls():
    items = [
        {'sale_item_type': 'a', 'sale_item_id': 1, 'item_id': 101, 'band_name': 'Artist', 'item_title': 'Title'},
        {'item_type': 'subscription', 'item_url': 'http://example.com'}
    ]
    urls = {'a1': 'http://download.com/1'}
    
    result = bd.merge_items_and_urls(items, urls)
    assert len(result) == 1
    assert 'a1' in result
    assert result['a1']['redownload_url'] == 'http://download.com/1'

def test_add_item_file_paths():
    bd.CONFIG['OUTPUT_DIR'] = 'out'
    bd.CONFIG['FILENAME_FORMAT'] = '{artist} - {title}'
    
    items = {
        'a1': {'item_id': 101, 'band_name': 'Artist', 'item_title': 'Title'},
        'a2': {'item_id': 102, 'band_name': 'Artist', 'item_title': 'Title'} # Duplicate name
    }
    
    bd.add_item_file_paths(items)
    
    assert items['a1']['file_path'] == os.path.join('out', 'Artist - Title-a1')
    assert items['a2']['file_path'] == os.path.join('out', 'Artist - Title-a2')
    
    items2 = {
        'a3': {'item_id': 103, 'band_name': 'Artist', 'item_title': 'Unique'}
    }
    bd.add_item_file_paths(items2)
    assert items2['a3']['file_path'] == os.path.join('out', 'Artist - Unique')

def test_download_exists(tmp_path, monkeypatch):
    file = tmp_path / "test.zip"
    file.write_bytes(b"0" * 1024 * 1024) # 1MB
    
    bd.CONFIG['FORCE'] = False
    
    # Matches size (0.15 tolerance)
    assert bd.download_exists(str(file), "1.0MB") is True
    
    # Doesn't match size
    assert bd.download_exists(str(file), "2.0MB") is False
    
    # No size provided
    assert bd.download_exists(str(file), "") is False
    
    # Force flag
    bd.CONFIG['FORCE'] = True
    # We need to mock TQDM write if we are verbose
    bd.CONFIG['VERBOSE'] = False
    assert bd.download_exists(str(file), "1.0MB") is False
    bd.CONFIG['FORCE'] = False
    
    # Non-existent file
    assert bd.download_exists("nonexistent", "1.0MB") is False
