# coding: utf8
from __future__ import unicode_literals

import bz2
import re
import srsly
import sys
import random
import datetime
import plac
from pathlib import Path

_unset = object()


class Reddit(object):
    """Stream cleaned comments from Reddit."""

    pre_format_re = re.compile(r"^[`*~]")
    post_format_re = re.compile(r"[`*~]$")
    url_re = re.compile(r"\[([^]]+)\]\(%%URL\)")
    link_re = re.compile(r"\[([^]]+)\]\(https?://[^\)]+\)")

    def __init__(self, file_path, meta_keys={"subreddit": "section"}):
        """
        file_path (unicode / Path): Path to archive or directory of archives.
        meta_keys (dict): Meta data key included in the Reddit corpus, mapped
            to display name in Prodigy meta.
        RETURNS (Reddit): The Reddit loader.
        """
        self.meta = meta_keys
        file_path = Path(file_path)
        if not file_path.exists():
            raise IOError("Can't find file path: {}".format(file_path))
        if not file_path.is_dir():
            self.files = [file_path]
        else:
            self.files = list(file_path.iterdir())

    def __iter__(self):
        for file_path in self.iter_files():
            with bz2.open(str(file_path)) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    comment = srsly.json_loads(line)
                    if self.is_valid(comment):
                        text = self.strip_tags(comment["body"])
                        yield {"text": text}

    def get_meta(self, item):
        return {name: item.get(key, "n/a") for key, name in self.meta.items()}

    def iter_files(self):
        for file_path in self.files:
            yield file_path

    def strip_tags(self, text):
        text = self.link_re.sub(r"\1", text)
        text = text.replace("&gt;", ">").replace("&lt;", "<")
        text = self.pre_format_re.sub("", text)
        text = self.post_format_re.sub("", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def is_valid(self, comment):
        return (
            comment["body"] is not None
            and comment["body"] != "[deleted]"
            and comment["body"] != "[removed]"
        )


def main(path):
    reddit = Reddit(path)
    for comment in reddit:
        print(srsly.json_dumps(comment))


if __name__ == "__main__":
    import socket

    try:
        BrokenPipeError
    except NameError:
        BrokenPipeError = socket.error
    try:
        plac.call(main)
    except BrokenPipeError:
        import os, sys

        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
