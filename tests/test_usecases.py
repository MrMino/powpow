from powpow import cat, grep


def test_from_file_to_grep(tmp_file):
    contents = "This will be grepped.\n"
    tmp_file.write_text(contents)
    assert cat(tmp_file, tmp_file, tmp_file) | grep("will be") == contents * 3
