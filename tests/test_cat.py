import itertools
import pytest

from pathlib import Path

from powpow import cat, CatResult


@pytest.fixture
def tmp_file(tmp_path):
    tmp_file = tmp_path / 'file'
    tmp_file.touch()
    return tmp_file


class TestCatInit:

    @pytest.fixture
    def two_tmp_files(self, tmp_path):
        tmp_files = [tmp_path / 'file', tmp_path / 'file']
        for f in tmp_files:
            f.touch()
        return tmp_files

    path_types = [Path, str]

    @pytest.mark.parametrize('path_type', path_types)
    def test_takes_filenames_of_different_types(self, path_type, tmp_file):
        cat(path_type(tmp_file))

    @pytest.mark.parametrize('path_types',
                             itertools.product(path_types, repeat=3))
    def test_takes_multiple_filenames_of_different_types(self, path_types,
                                                         tmp_file):
        typ_a, typ_b, typ_c = path_types
        cat(typ_a(tmp_file), typ_b(tmp_file), typ_c(tmp_file))

    def test_returns_contents_of_file(self, tmp_file):
        contents = "contents"
        tmp_file.write_text(contents)
        assert str(cat(tmp_file)) == contents

    def test_returns_CatResult(self, tmp_file):
        assert isinstance(cat(tmp_file), CatResult)


class TestCatResult:
    def test_paths_property_lists_paths(self, tmp_file):
        paths = (tmp_file, tmp_file, tmp_file)
        assert cat(*paths).paths == paths

    def test_contents_property_lists_out_contents(self, tmp_file):
        contents = "contents"
        tmp_file.write_text(contents)
        paths = [tmp_file, tmp_file, tmp_file]
        contents = ("contents", "contents", "contents")
        assert cat(*paths).contents == contents

    def test_cat_result_strs_to_catenated_contents(self, tmp_file):
        contents = "contents"
        tmp_file.write_text(contents)
        paths = [tmp_file, tmp_file, tmp_file]
        catenated = "contentscontentscontents"
        assert str(cat(*paths)) == catenated
