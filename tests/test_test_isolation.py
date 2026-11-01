'''Protect source fixtures and ensure outputs cannot be reused across tests.'''
from pathlib import Path

from pyDEA.core.data_processing.xlsx_workbook import XlsxWorkbook


def test_output_is_created_only_in_sandbox(tmp_path):
    source_directory = Path(__file__).resolve().parent
    source = source_directory / 'test_peel_the_onion.xlsx'
    original = source.read_bytes()
    output = Path('tests/test_peel_the_onion.xlsx')
    assert Path.cwd() == tmp_path
    assert not output.exists()
    workbook = XlsxWorkbook()
    workbook.add_sheet('Result').write(0, 0, 'sandbox only')
    workbook.save(str(output))
    assert output.is_file()
    assert source.read_bytes() == original


def test_input_fixtures_are_independent_copies(tmp_path):
    source = Path(__file__).resolve().parent / 'test_file_for_data_save.xlsx'
    original = source.read_bytes()
    copied = Path('tests/test_file_for_data_save.xlsx')
    assert copied.resolve().is_relative_to(tmp_path)
    assert not copied.is_symlink()
    assert copied.read_bytes() == original
    copied.write_bytes(b'changed only inside this test')
    assert source.read_bytes() == original