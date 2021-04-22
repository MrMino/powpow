import pytest


@pytest.fixture
def tmp_file(tmp_path):
    tmp_file = tmp_path / 'file'
    tmp_file.touch()
    return tmp_file
