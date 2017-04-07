from __future__ import unicode_literals

# The use of this module turns out to be important, to avoid pathological
# back-tracking. See Issue #957
import regex

# URL validation regex courtesy of: https://mathiasbynens.be/demo/url-regex
# A few minor mods to this regex to account for use cases represented in test_urls
_URL_PATTERN = (
    r"^"
    # in order to support the prefix tokenization (see prefix test cases in test_urls).
    r"(?=[\w])"
    # protocol identifier
    r"(?:(?:https?|ftp|mailto)://)?"
    # user:pass authentication
    r"(?:\S+(?::\S*)?@)?"
    r"(?:"
    # IP address exclusion
    # private & local networks
    r"(?!(?:10|127)(?:\.\d{1,3}){3})"
    r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
    r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    # MH: Do we really need this? Seems excessive, and seems to have caused
    # Issue #957
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
    r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
    r"|"
    # host name
    r"(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)"
    # domain name
    r"(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*"
    # TLD identifier
    r"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
    r")"
    # port number
    r"(?::\d{2,5})?"
    # resource path
    r"(?:/\S*)?"
    # query parameters
    r"\??(:?\S*)?"
    # in order to support the suffix tokenization (see suffix test cases in test_urls),
    r"(?<=[\w/])"
    r"$"
).strip()

TOKEN_MATCH = regex.compile(_URL_PATTERN, regex.UNICODE).match

__all__ = ['TOKEN_MATCH']
