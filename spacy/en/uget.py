import os
import time
import io
import math
import re

try:
    from urllib.parse import urlparse
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, urlparse, Request, HTTPError


class UnknownContentLengthException(Exception): pass
class InvalidChecksumException(Exception): pass
class UnsupportedHTTPCodeException(Exception): pass
class InvalidOffsetException(Exception): pass
class MissingChecksumHeader(Exception): pass


CHUNK_SIZE = 16 * 1024


class RateSampler(object):
    def __init__(self, period=1):
        self.rate = None
        self.reset = True
        self.period = period

    def __enter__(self):
        if self.reset:
            self.reset = False
            self.start = time.time()
            self.counter = 0

    def __exit__(self, type, value, traceback):
        elapsed = time.time() - self.start
        if elapsed >= self.period:
            self.reset = True
            self.rate = float(self.counter) / elapsed

    def update(self, value):
        self.counter += value

    def format(self, unit="MB"):
        if self.rate is None:
            return None

        divisor = {'MB': 1048576, 'kB': 1024}
        return "%0.2f%s/s" % (self.rate / divisor[unit], unit)


class TimeEstimator(object):
    def __init__(self, cooldown=1):
        self.cooldown = cooldown
        self.start = time.time()
        self.time_left = None

    def update(self, bytes_read, total_size):
        elapsed = time.time() - self.start
        if elapsed > self.cooldown:
            self.time_left = math.ceil(elapsed * total_size /
                                       bytes_read - elapsed)

    def format(self):
        if self.time_left is None:
            return None

        res = "eta "
        if self.time_left / 60 >= 1:
            res += "%dm " % (self.time_left / 60)
        return res + "%ds" % (self.time_left % 60)


def format_bytes_read(bytes_read, unit="MB"):
    divisor = {'MB': 1048576, 'kB': 1024}
    return "%0.2f%s" % (float(bytes_read) / divisor[unit], unit)


def format_percent(bytes_read, total_size):
    percent = round(bytes_read * 100.0 / total_size, 2)
    return "%0.2f%%" % percent


def get_content_range(response):
    content_range = response.headers.get('Content-Range', "").strip()
    if content_range:
        m = re.match(r"bytes (\d+)-(\d+)/(\d+)", content_range)
        if m:
            return [int(v) for v in m.groups()]


def get_content_length(response):
    if 'Content-Length' not in response.headers:
        raise UnknownContentLengthException
    return int(response.headers.get('Content-Length').strip())


def get_url_meta(url, checksum_header=None):
    class HeadRequest(Request):
        def get_method(self):
            return "HEAD"

    r = urlopen(HeadRequest(url))
    res = {'size': get_content_length(r)}

    if checksum_header:
        value = r.headers.get(checksum_header)
        if value:
            res['checksum'] = value

    r.close()
    return res


def progress(console, bytes_read, total_size, transfer_rate, eta):
    fields = [
        format_bytes_read(bytes_read),
        format_percent(bytes_read, total_size),
        transfer_rate.format(),
        eta.format(),
        " " * 10,
    ]
    console.write("Downloaded %s\r" % " ".join(filter(None, fields)))
    console.flush()


def read_request(request, offset=0, console=None,
                 progress_func=None, write_func=None):
    # support partial downloads
    if offset > 0:
        request.add_header('Range', "bytes=%s-" % offset)

    try:
        response = urlopen(request)
    except HTTPError as e:
        if e.code == 416:  # Requested Range Not Satisfiable
            raise InvalidOffsetException

        # TODO add http error handling here
        raise UnsupportedHTTPCodeException(e.code)

    total_size = get_content_length(response) + offset
    bytes_read = offset

    # sanity checks
    if response.code == 200:  # OK
        assert offset == 0
    elif response.code == 206:  # Partial content
        range_start, range_end, range_total = get_content_range(response)
        assert range_start == offset
        assert range_total == total_size
        assert range_end + 1 - range_start == total_size - bytes_read
    else:
        raise UnsupportedHTTPCodeException(response.code)

    eta = TimeEstimator()
    transfer_rate = RateSampler()

    if console:
        if offset > 0:
            console.write("Continue downloading...\n")
        else:
            console.write("Downloading...\n")

    while True:
        with transfer_rate:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                if progress_func and console:
                    console.write('\n')
                break

            bytes_read += len(chunk)

            transfer_rate.update(len(chunk))
            eta.update(bytes_read - offset, total_size - offset)

        if progress_func and console:
            progress_func(console, bytes_read, total_size, transfer_rate, eta)

        if write_func:
            write_func(chunk)

    response.close()
    assert bytes_read == total_size
    return response


def download(url, path=".",
             checksum=None, checksum_header=None,
             headers=None, console=None):

    if os.path.isdir(path):
        path = os.path.join(path, url.rsplit('/', 1)[1])
    path = os.path.abspath(path)

    with io.open(path, "a+b") as f:
        size = f.tell()

        # update checksum of partially downloaded file
        if checksum:
            f.seek(0, os.SEEK_SET)
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                checksum.update(chunk)

        def write(chunk):
            if checksum:
                checksum.update(chunk)
            f.write(chunk)

        request = Request(url)

        # request headers
        if headers:
            for key, value in headers.items():
                request.add_header(key, value)

        try:
            response = read_request(request,
                                    offset=size,
                                    console=console,
                                    progress_func=progress,
                                    write_func=write)
        except InvalidOffsetException:
            response = None

        if checksum:
            if response:
                origin_checksum = response.headers.get(checksum_header)
            else:
                # check whether file is already complete
                meta = get_url_meta(url, checksum_header)
                origin_checksum = meta.get('checksum')

            if origin_checksum is None:
                raise MissingChecksumHeader

            if checksum.hexdigest() != origin_checksum:
                raise InvalidChecksumException

            if console:
                console.write("checksum/sha256 OK\n")

    return path
