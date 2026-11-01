'''Run legacy relative-path tests in disposable, per-test working directories.'''
from pathlib import Path
import shutil

import pytest


FIXTURE_DIRECTORY = Path(__file__).resolve().parent


@pytest.fixture(autouse=True)
def isolated_working_directory(tmp_path, monkeypatch):
    '''Copy inputs, never old outputs, so stale results cannot make tests pass.

    Keep the historical tests/... layout while isolating XLSX writes, logs,
    pickles and cleanup/rmtree calls from both the checkout and other tests.
    Ordinary copies (not symlinks) also protect fixtures that get overwritten.
    '''
    destination = tmp_path / 'tests'
    destination.mkdir()
    for source in FIXTURE_DIRECTORY.iterdir():
        if source.suffix not in {'.xlsx', '.csv', '.txt'}:
            continue
        if (source.name.startswith('test_') and
                source.name != 'test_file_for_data_save.xlsx'):
            continue
        shutil.copy2(source, destination / source.name)
    monkeypatch.chdir(tmp_path)