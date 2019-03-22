import pytest
import re
from ... import compat

prefix_search = (
    b"^\xc2\xa7|^%|^=|^\xe2\x80\x94|^\xe2\x80\x93|^\\+(?![0-9])"
    b"|^\xe2\x80\xa6|^\xe2\x80\xa6\xe2\x80\xa6|^,|^:|^;|^\\!|^\\?"
    b"|^\xc2\xbf|^\xd8\x9f|^\xc2\xa1|^\\(|^\\)|^\\[|^\\]|^\\{|^\\}"
    b"|^<|^>|^_|^#|^\\*|^&|^\xe3\x80\x82|^\xef\xbc\x9f|^\xef\xbc\x81|"
    b"^\xef\xbc\x8c|^\xe3\x80\x81|^\xef\xbc\x9b|^\xef\xbc\x9a|"
    b"^\xef\xbd\x9e|^\xc2\xb7|^\xe0\xa5\xa4|^\xd8\x8c|^\xd8\x9b|"
    b"^\xd9\xaa|^\\.\\.+|^\xe2\x80\xa6|^\\'|^\"|^\xe2\x80\x9d|"
    b"^\xe2\x80\x9c|^`|^\xe2\x80\x98|^\xc2\xb4|^\xe2\x80\x99|"
    b"^\xe2\x80\x9a|^,|^\xe2\x80\x9e|^\xc2\xbb|^\xc2\xab|^\xe3\x80\x8c|"
    b"^\xe3\x80\x8d|^\xe3\x80\x8e|^\xe3\x80\x8f|^\xef\xbc\x88|"
    b"^\xef\xbc\x89|^\xe3\x80\x94|^\xe3\x80\x95|^\xe3\x80\x90|"
    b"^\xe3\x80\x91|^\xe3\x80\x8a|^\xe3\x80\x8b|^\xe3\x80\x88|"
    b"^\xe3\x80\x89|^\\$|^\xc2\xa3|^\xe2\x82\xac|^\xc2\xa5|^\xe0\xb8\xbf|"
    b"^US\\$|^C\\$|^A\\$|^\xe2\x82\xbd|^\xef\xb7\xbc|^\xe2\x82\xb4|"
    b"^[\\u00A6\\u00A9\\u00AE\\u00B0\\u0482\\u058D\\u058E\\u060E\\u060F"
    b"\\u06DE\\u06E9\\u06FD\\u06FE\\u07F6\\u09FA\\u0B70\\u0BF3-\\u0BF8"
    b"\\u0BFA\\u0C7F\\u0D4F\\u0D79\\u0F01-\\u0F03\\u0F13\\u0F15-\\u0F17"
    b"\\u0F1A-\\u0F1F\\u0F34\\u0F36\\u0F38\\u0FBE-\\u0FC5\\u0FC7-\\u0FCC"
    b"\\u0FCE\\u0FCF\\u0FD5-\\u0FD8\\u109E\\u109F\\u1390-\\u1399\\u1940"
    b"\\u19DE-\\u19FF\\u1B61-\\u1B6A\\u1B74-\\u1B7C\\u2100\\u2101\\u2103"
    b"-\\u2106\\u2108\\u2109\\u2114\\u2116\\u2117\\u211E-\\u2123\\u2125"
    b"\\u2127\\u2129\\u212E\\u213A\\u213B\\u214A\\u214C\\u214D\\u214F"
    b"\\u218A\\u218B\\u2195-\\u2199\\u219C-\\u219F\\u21A1\\u21A2\\u21A4"
    b"\\u21A5\\u21A7-\\u21AD\\u21AF-\\u21CD\\u21D0\\u21D1\\u21D3\\u21D5"
    b"-\\u21F3\\u2300-\\u2307\\u230C-\\u231F\\u2322-\\u2328\\u232B"
    b"-\\u237B\\u237D-\\u239A\\u23B4-\\u23DB\\u23E2-\\u2426\\u2440"
    b"-\\u244A\\u249C-\\u24E9\\u2500-\\u25B6\\u25B8-\\u25C0\\u25C2"
    b"-\\u25F7\\u2600-\\u266E\\u2670-\\u2767\\u2794-\\u27BF\\u2800"
    b"-\\u28FF\\u2B00-\\u2B2F\\u2B45\\u2B46\\u2B4D-\\u2B73\\u2B76"
    b"-\\u2B95\\u2B98-\\u2BC8\\u2BCA-\\u2BFE\\u2CE5-\\u2CEA\\u2E80"
    b"-\\u2E99\\u2E9B-\\u2EF3\\u2F00-\\u2FD5\\u2FF0-\\u2FFB\\u3004"
    b"\\u3012\\u3013\\u3020\\u3036\\u3037\\u303E\\u303F\\u3190\\u3191"
    b"\\u3196-\\u319F\\u31C0-\\u31E3\\u3200-\\u321E\\u322A-\\u3247\\u3250"
    b"\\u3260-\\u327F\\u328A-\\u32B0\\u32C0-\\u32FE\\u3300-\\u33FF\\u4DC0"
    b"-\\u4DFF\\uA490-\\uA4C6\\uA828-\\uA82B\\uA836\\uA837\\uA839\\uAA77"
    b"-\\uAA79\\uFDFD\\uFFE4\\uFFE8\\uFFED\\uFFEE\\uFFFC\\uFFFD\\U00010137"
    b"-\\U0001013F\\U00010179-\\U00010189\\U0001018C-\\U0001018E"
    b"\\U00010190-\\U0001019B\\U000101A0\\U000101D0-\\U000101FC\\U00010877"
    b"\\U00010878\\U00010AC8\\U0001173F\\U00016B3C-\\U00016B3F\\U00016B45"
    b"\\U0001BC9C\\U0001D000-\\U0001D0F5\\U0001D100-\\U0001D126\\U0001D129"
    b"-\\U0001D164\\U0001D16A-\\U0001D16C\\U0001D183\\U0001D184\\U0001D18C"
    b"-\\U0001D1A9\\U0001D1AE-\\U0001D1E8\\U0001D200-\\U0001D241\\U0001D245"
    b"\\U0001D300-\\U0001D356\\U0001D800-\\U0001D9FF\\U0001DA37-\\U0001DA3A"
    b"\\U0001DA6D-\\U0001DA74\\U0001DA76-\\U0001DA83\\U0001DA85\\U0001DA86"
    b"\\U0001ECAC\\U0001F000-\\U0001F02B\\U0001F030-\\U0001F093\\U0001F0A0"
    b"-\\U0001F0AE\\U0001F0B1-\\U0001F0BF\\U0001F0C1-\\U0001F0CF\\U0001F0D1"
    b"-\\U0001F0F5\\U0001F110-\\U0001F16B\\U0001F170-\\U0001F1AC\\U0001F1E6"
    b"-\\U0001F202\\U0001F210-\\U0001F23B\\U0001F240-\\U0001F248\\U0001F250"
    b"\\U0001F251\\U0001F260-\\U0001F265\\U0001F300-\\U0001F3FA\\U0001F400"
    b"-\\U0001F6D4\\U0001F6E0-\\U0001F6EC\\U0001F6F0-\\U0001F6F9\\U0001F700"
    b"-\\U0001F773\\U0001F780-\\U0001F7D8\\U0001F800-\\U0001F80B\\U0001F810"
    b"-\\U0001F847\\U0001F850-\\U0001F859\\U0001F860-\\U0001F887\\U0001F890"
    b"-\\U0001F8AD\\U0001F900-\\U0001F90B\\U0001F910-\\U0001F93E\\U0001F940"
    b"-\\U0001F970\\U0001F973-\\U0001F976\\U0001F97A\\U0001F97C-\\U0001F9A2"
    b"\\U0001F9B0-\\U0001F9B9\\U0001F9C0-\\U0001F9C2\\U0001F9D0-\\U0001F9FF"
    b"\\U0001FA60-\\U0001FA6D]"
)


if compat.is_python2:
    # If we have this test in Python 3, pytest chokes, as it can't print the
    # string above in the xpass message.
    def test_issue3356():
        pattern = re.compile(compat.unescape_unicode(prefix_search.decode("utf8")))
        assert not pattern.search(u"hello")
