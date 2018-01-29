from __future__ import unicode_literals

from ... cli import download

def test_issue1904(capsys):
    download('en')
    out, err = capsys.readouterr()
    assert "Linking successful" in out