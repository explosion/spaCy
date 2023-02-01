import pytest
from ...ml.richfeatureextractor import get_character_combination_hashes

EMPTY_HASH_VALUE = 0xCBF29CE484222325
FNV1A_OFFSET_BASIS = 0xCBF29CE484222325
FNV1A_PRIME = 0x00000100000001B3


def _get_fnv1a_hash(input: bytes) -> int:
    hash_val = FNV1A_OFFSET_BASIS
    length = len(input)
    offset = 0

    while offset < length:
        hash_val ^= input[offset]
        hash_val *= FNV1A_PRIME
        hash_val %= 2**64
        offset += 1
    return hash_val


def test_fnv1a_hash():
    """Checks the conformity of the 64-bit FNV1A implementation with
    http://www.isthe.com/chongo/src/fnv/test_fnv.c.
    The method called here, _get_fnv1a_hash(), is only used in testing;
    in production code, the hashing is performed in a fashion that is interweaved
    with other logic. The conformity of the production code is demonstrated by the
    character combination hash tests, where hashes produced by the production code
    are tested for equality against hashes produced by _get_fnv1a_hash().
    """
    INPUTS = [
        b"",
        b"a",
        b"b",
        b"c",
        b"d",
        b"e",
        b"f",
        b"fo",
        b"foo",
        b"foob",
        b"fooba",
        b"foobar",
        b"\x00",
        b"a\x00",
        b"b\x00",
        b"c\x00",
        b"d\x00",
        b"e\x00",
        b"f\x00",
        b"fo\x00",
        b"foo\x00",
        b"foob\x00",
        b"fooba\x00",
        b"foobar\x00",
        b"ch",
        b"cho",
        b"chon",
        b"chong",
        b"chongo",
        b"chongo ",
        b"chongo w",
        b"chongo wa",
        b"chongo was",
        b"chongo was ",
        b"chongo was h",
        b"chongo was he",
        b"chongo was her",
        b"chongo was here",
        b"chongo was here!",
        b"chongo was here!\n",
        b"ch\x00",
        b"cho\x00",
        b"chon\x00",
        b"chong\x00",
        b"chongo\x00",
        b"chongo \x00",
        b"chongo w\x00",
        b"chongo wa\x00",
        b"chongo was\x00",
        b"chongo was \x00",
        b"chongo was h\x00",
        b"chongo was he\x00",
        b"chongo was her\x00",
        b"chongo was here\x00",
        b"chongo was here!\x00",
        b"chongo was here!\n\x00",
        b"cu",
        b"cur",
        b"curd",
        b"curds",
        b"curds ",
        b"curds a",
        b"curds an",
        b"curds and",
        b"curds and ",
        b"curds and w",
        b"curds and wh",
        b"curds and whe",
        b"curds and whey",
        b"curds and whey\n",
        b"cu\x00",
        b"cur\x00",
        b"curd\x00",
        b"curds\x00",
        b"curds \x00",
        b"curds a\x00",
        b"curds an\x00",
        b"curds and\x00",
        b"curds and \x00",
        b"curds and w\x00",
        b"curds and wh\x00",
        b"curds and whe\x00",
        b"curds and whey\x00",
        b"curds and whey\n\x00",
        b"hi",
        b"hi\x00",
        b"hello",
        b"hello\x00",
        b"\xff\x00\x00\x01",
        b"\x01\x00\x00\xff",
        b"\xff\x00\x00\x02",
        b"\x02\x00\x00\xff",
        b"\xff\x00\x00\x03",
        b"\x03\x00\x00\xff",
        b"\xff\x00\x00\x04",
        b"\x04\x00\x00\xff",
        b"\x40\x51\x4e\x44",
        b"\x44\x4e\x51\x40",
        b"\x40\x51\x4e\x4a",
        b"\x4a\x4e\x51\x40",
        b"\x40\x51\x4e\x54",
        b"\x54\x4e\x51\x40",
        b"127.0.0.1",
        b"127.0.0.1\x00",
        b"127.0.0.2",
        b"127.0.0.2\x00",
        b"127.0.0.3",
        b"127.0.0.3\x00",
        b"64.81.78.68",
        b"64.81.78.68\x00",
        b"64.81.78.74",
        b"64.81.78.74\x00",
        b"64.81.78.84",
        b"64.81.78.84\x00",
        b"feedface",
        b"feedface\x00",
        b"feedfacedaffdeed",
        b"feedfacedaffdeed\x00",
        b"feedfacedeadbeef",
        b"feedfacedeadbeef\x00",
        b"line 1\nline 2\nline 3",
        b"chongo <Landon Curt Noll> /\\../\\",
        b"chongo <Landon Curt Noll> /\\../\\\x00",
        b"chongo (Landon Curt Noll) /\\../\\",
        b"chongo (Landon Curt Noll) /\\../\\\x00",
        b"http://antwrp.gsfc.nasa.gov/apod/astropix.html",
        b"http://en.wikipedia.org/wiki/Fowler_Noll_Vo_hash",
        b"http://epod.usra.edu/",
        b"http://exoplanet.eu/",
        b"http://hvo.wr.usgs.gov/cam3/",
        b"http://hvo.wr.usgs.gov/cams/HMcam/",
        b"http://hvo.wr.usgs.gov/kilauea/update/deformation.html",
        b"http://hvo.wr.usgs.gov/kilauea/update/images.html",
        b"http://hvo.wr.usgs.gov/kilauea/update/maps.html",
        b"http://hvo.wr.usgs.gov/volcanowatch/current_issue.html",
        b"http://neo.jpl.nasa.gov/risk/",
        b"http://norvig.com/21-days.html",
        b"http://primes.utm.edu/curios/home.php",
        b"http://slashdot.org/",
        b"http://tux.wr.usgs.gov/Maps/155.25-19.5.html",
        b"http://volcano.wr.usgs.gov/kilaueastatus.php",
        b"http://www.avo.alaska.edu/activity/Redoubt.php",
        b"http://www.dilbert.com/fast/",
        b"http://www.fourmilab.ch/gravitation/orbits/",
        b"http://www.fpoa.net/",
        b"http://www.ioccc.org/index.html",
        b"http://www.isthe.com/cgi-bin/number.cgi",
        b"http://www.isthe.com/chongo/bio.html",
        b"http://www.isthe.com/chongo/index.html",
        b"http://www.isthe.com/chongo/src/calc/lucas-calc",
        b"http://www.isthe.com/chongo/tech/astro/venus2004.html",
        b"http://www.isthe.com/chongo/tech/astro/vita.html",
        b"http://www.isthe.com/chongo/tech/comp/c/expert.html",
        b"http://www.isthe.com/chongo/tech/comp/calc/index.html",
        b"http://www.isthe.com/chongo/tech/comp/fnv/index.html",
        b"http://www.isthe.com/chongo/tech/math/number/howhigh.html",
        b"http://www.isthe.com/chongo/tech/math/number/number.html",
        b"http://www.isthe.com/chongo/tech/math/prime/mersenne.html",
        b"http://www.isthe.com/chongo/tech/math/prime/mersenne.html#largest",
        b"http://www.lavarnd.org/cgi-bin/corpspeak.cgi",
        b"http://www.lavarnd.org/cgi-bin/haiku.cgi",
        b"http://www.lavarnd.org/cgi-bin/rand-none.cgi",
        b"http://www.lavarnd.org/cgi-bin/randdist.cgi",
        b"http://www.lavarnd.org/index.html",
        b"http://www.lavarnd.org/what/nist-test.html",
        b"http://www.macosxhints.com/",
        b"http://www.mellis.com/",
        b"http://www.nature.nps.gov/air/webcams/parks/havoso2alert/havoalert.cfm",
        b"http://www.nature.nps.gov/air/webcams/parks/havoso2alert/timelines_24.cfm",
        b"http://www.paulnoll.com/",
        b"http://www.pepysdiary.com/",
        b"http://www.sciencenews.org/index/home/activity/view",
        b"http://www.skyandtelescope.com/",
        b"http://www.sput.nl/~rob/sirius.html",
        b"http://www.systemexperts.com/",
        b"http://www.tq-international.com/phpBB3/index.php",
        b"http://www.travelquesttours.com/index.htm",
        b"http://www.wunderground.com/global/stations/89606.html",
        b"21701" * 10,
        b"M21701" * 10,
        b"2^21701-1" * 10,
        b"\x54\xc5" * 10,
        b"\xc5\x54" * 10,
        b"23209" * 10,
        b"M23209" * 10,
        b"2^23209-1" * 10,
        b"\x5a\xa9" * 10,
        b"\xa9\x5a" * 10,
        b"391581216093" * 10,
        b"391581*2^216093-1" * 10,
        b"\x05\xf9\x9d\x03\x4c\x81" * 10,
        b"FEDCBA9876543210" * 10,
        b"\xfe\xdc\xba\x98\x76\x54\x32\x10" * 10,
        b"EFCDAB8967452301" * 10,
        b"\xef\xcd\xab\x89\x67\x45\x23\x01" * 10,
        b"0123456789ABCDEF" * 10,
        b"\x01\x23\x45\x67\x89\xab\xcd\xef" * 10,
        b"1032547698BADCFE" * 10,
        b"\x10\x32\x54\x76\x98\xba\xdc\xfe" * 10,
        b"\x00" * 500,
        b"\x07" * 500,
        b"~" * 500,
        b"\x7f" * 500,
    ]

    OUTPUTS = [
        EMPTY_HASH_VALUE,
        0xAF63DC4C8601EC8C,
        0xAF63DF4C8601F1A5,
        0xAF63DE4C8601EFF2,
        0xAF63D94C8601E773,
        0xAF63D84C8601E5C0,
        0xAF63DB4C8601EAD9,
        0x08985907B541D342,
        0xDCB27518FED9D577,
        0xDD120E790C2512AF,
        0xCAC165AFA2FEF40A,
        0x85944171F73967E8,
        0xAF63BD4C8601B7DF,
        0x089BE207B544F1E4,
        0x08A61407B54D9B5F,
        0x08A2AE07B54AB836,
        0x0891B007B53C4869,
        0x088E4A07B5396540,
        0x08987C07B5420EBB,
        0xDCB28A18FED9F926,
        0xDD1270790C25B935,
        0xCAC146AFA2FEBF5D,
        0x8593D371F738ACFE,
        0x34531CA7168B8F38,
        0x08A25607B54A22AE,
        0xF5FAF0190CF90DF3,
        0xF27397910B3221C7,
        0x2C8C2B76062F22E0,
        0xE150688C8217B8FD,
        0xF35A83C10E4F1F87,
        0xD1EDD10B507344D0,
        0x2A5EE739B3DDB8C3,
        0xDCFB970CA1C0D310,
        0x4054DA76DAA6DA90,
        0xF70A2FF589861368,
        0x4C628B38AED25F17,
        0x9DD1F6510F78189F,
        0xA3DE85BD491270CE,
        0x858E2FA32A55E61D,
        0x46810940EFF5F915,
        0xF5FADD190CF8EDAA,
        0xF273ED910B32B3E9,
        0x2C8C5276062F6525,
        0xE150B98C821842A0,
        0xF35AA3C10E4F55E7,
        0xD1ED680B50729265,
        0x2A5F0639B3DDED70,
        0xDCFBAA0CA1C0F359,
        0x4054BA76DAA6A430,
        0xF709C7F5898562B0,
        0x4C62E638AED2F9B8,
        0x9DD1A8510F779415,
        0xA3DE2ABD4911D62D,
        0x858E0EA32A55AE0A,
        0x46810F40EFF60347,
        0xC33BCE57BEF63EAF,
        0x08A24307B54A0265,
        0xF5B9FD190CC18D15,
        0x4C968290ACE35703,
        0x07174BD5C64D9350,
        0x5A294C3FF5D18750,
        0x05B3C1AEB308B843,
        0xB92A48DA37D0F477,
        0x73CDDDCCD80EBC49,
        0xD58C4C13210A266B,
        0xE78B6081243EC194,
        0xB096F77096A39F34,
        0xB425C54FF807B6A3,
        0x23E520E2751BB46E,
        0x1A0B44CCFE1385EC,
        0xF5BA4B190CC2119F,
        0x4C962690ACE2BAAF,
        0x0716DED5C64CDA19,
        0x5A292C3FF5D150F0,
        0x05B3E0AEB308ECF0,
        0xB92A5EDA37D119D9,
        0x73CE41CCD80F6635,
        0xD58C2C132109F00B,
        0xE78BAF81243F47D1,
        0xB0968F7096A2EE7C,
        0xB425A84FF807855C,
        0x23E4E9E2751B56F9,
        0x1A0B4ECCFE1396EA,
        0x54ABD453BB2C9004,
        0x08BA5F07B55EC3DA,
        0x337354193006CB6E,
        0xA430D84680AABD0B,
        0xA9BC8ACCA21F39B1,
        0x6961196491CC682D,
        0xAD2BB1774799DFE9,
        0x6961166491CC6314,
        0x8D1BB3904A3B1236,
        0x6961176491CC64C7,
        0xED205D87F40434C7,
        0x6961146491CC5FAE,
        0xCD3BAF5E44F8AD9C,
        0xE3B36596127CD6D8,
        0xF77F1072C8E8A646,
        0xE3B36396127CD372,
        0x6067DCE9932AD458,
        0xE3B37596127CF208,
        0x4B7B10FA9FE83936,
        0xAABAFE7104D914BE,
        0xF4D3180B3CDE3EDA,
        0xAABAFD7104D9130B,
        0xF4CFB20B3CDB5BB1,
        0xAABAFC7104D91158,
        0xF4CC4C0B3CD87888,
        0xE729BAC5D2A8D3A7,
        0x74BC0524F4DFA4C5,
        0xE72630C5D2A5B352,
        0x6B983224EF8FB456,
        0xE73042C5D2AE266D,
        0x8527E324FDEB4B37,
        0x0A83C86FEE952ABC,
        0x7318523267779D74,
        0x3E66D3D56B8CACA1,
        0x956694A5C0095593,
        0xCAC54572BB1A6FC8,
        0xA7A4C9F3EDEBF0D8,
        0x7829851FAC17B143,
        0x2C8F4C9AF81BCF06,
        0xD34E31539740C732,
        0x3605A2AC253D2DB1,
        0x08C11B8346F4A3C3,
        0x6BE396289CE8A6DA,
        0xD9B957FB7FE794C5,
        0x05BE33DA04560A93,
        0x0957F1577BA9747C,
        0xDA2CC3ACC24FBA57,
        0x74136F185B29E7F0,
        0xB2F2B4590EDB93B2,
        0xB3608FCE8B86AE04,
        0x4A3A865079359063,
        0x5B3A7EF496880A50,
        0x48FAE3163854C23B,
        0x07AAA640476E0B9A,
        0x2F653656383A687D,
        0xA1031F8E7599D79C,
        0xA31908178FF92477,
        0x097EDF3C14C3FB83,
        0xB51CA83FEAA0971B,
        0xDD3C0D96D784F2E9,
        0x86CD26A9EA767D78,
        0xE6B215FF54A30C18,
        0xEC5B06A1C5531093,
        0x45665A929F9EC5E5,
        0x8C7609B4A9F10907,
        0x89AAC3A491F0D729,
        0x32CE6B26E0F4A403,
        0x614AB44E02B53E01,
        0xFA6472EB6EEF3290,
        0x9E5D75EB1948EB6A,
        0xB6D12AD4A8671852,
        0x88826F56EBA07AF1,
        0x44535BF2645BC0FD,
        0x169388FFC21E3728,
        0xF68AAC9E396D8224,
        0x8E87D7E7472B3883,
        0x295C26CAA8B423DE,
        0x322C814292E72176,
        0x8A06550EB8AF7268,
        0xEF86D60E661BCF71,
        0x9E5426C87F30EE54,
        0xF1EA8AA826FD047E,
        0x0BABAF9A642CB769,
        0x4B3341D4068D012E,
        0xD15605CBC30A335C,
        0x5B21060AED8412E5,
        0x45E2CDA1CE6F4227,
        0x50AE3745033AD7D4,
        0xAA4588CED46BF414,
        0xC1B0056C4A95467E,
        0x56576A71DE8B4089,
        0xBF20965FA6DC927E,
        0x569F8383C2040882,
        0xE1E772FBA08FECA0,
        0x4CED94AF97138AC4,
        0xC4112FFB337A82FB,
        0xD64A4FD41DE38B7D,
        0x4CFC32329EDEBCBB,
        0x0803564445050395,
        0xAA1574ECF4642FFD,
        0x694BC4E54CC315F9,
        0xA3D7CB273B011721,
        0x577C2F8B6115BFA5,
        0xB7EC8C1A769FB4C1,
        0x5D5CFCE63359AB19,
        0x33B96C3CD65B5F71,
        0xD845097780602BB9,
        0x84D47645D02DA3D5,
        0x83544F33B58773A5,
        0x9175CBB2160836C5,
        0xC71B3BC175E72BC5,
        0x636806AC222EC985,
        0xB6EF0E6950F52ED5,
        0xEAD3D8A0F3DFDAA5,
        0x922908FE9A861BA5,
        0x6D4821DE275FD5C5,
        0x1FE3FCE62BD816B5,
        0xC23E9FCCD6F70591,
        0xC1AF12BDFE16B5B5,
        0x39E9F18F2F85E221,
    ]

    assert len(INPUTS) == len(OUTPUTS)
    for i in range(len(INPUTS)):
        assert _get_fnv1a_hash(INPUTS[i]) == OUTPUTS[i]


def _encode_and_hash(input: str, *, reverse: bool = False) -> int:
    encoded_input = input.encode("UTF-8")
    if reverse:
        encoded_input = encoded_input[::-1]
    return _get_fnv1a_hash(encoded_input)


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_character_combination_hashes_good_case(en_tokenizer, case_sensitive):
    doc = en_tokenizer("spaCy✨ and Prodigy")

    hashes = get_character_combination_hashes(
        doc=doc,
        case_sensitive=case_sensitive,
        p_lengths=bytes(
            (
                1,
                3,
                4,
            )
        ),
        s_lengths=bytes(
            (
                2,
                3,
                4,
                5,
            )
        ),
    )
    assert hashes[0][0] == _encode_and_hash("s")
    assert hashes[0][1] == _encode_and_hash("spa")
    assert hashes[0][2] == _encode_and_hash("spaC" if case_sensitive else "spac")
    assert hashes[0][3] == _encode_and_hash("yC" if case_sensitive else "yc")
    assert hashes[0][4] == _encode_and_hash("yCa" if case_sensitive else "yca")
    assert hashes[0][5] == _encode_and_hash("yCap" if case_sensitive else "ycap")
    assert hashes[0][6] == _encode_and_hash("yCaps" if case_sensitive else "ycaps")
    assert hashes[1][0] == _encode_and_hash("✨")
    assert hashes[1][1] == _encode_and_hash("✨")
    assert hashes[1][2] == _encode_and_hash("✨")
    assert hashes[1][3] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][4] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][5] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][6] == _encode_and_hash("✨", reverse=True)
    assert hashes[2][0] == _encode_and_hash("a")
    assert hashes[2][1] == _encode_and_hash("and")
    assert hashes[2][2] == _encode_and_hash("and")
    assert hashes[2][3] == _encode_and_hash("dn")
    assert hashes[2][4] == _encode_and_hash("dna")
    assert hashes[2][5] == _encode_and_hash("dna")
    assert hashes[2][6] == _encode_and_hash("dna")
    assert hashes[3][0] == _encode_and_hash("P" if case_sensitive else "p")
    assert hashes[3][1] == _encode_and_hash("Pro" if case_sensitive else "pro")
    assert hashes[3][2] == _encode_and_hash("Prod" if case_sensitive else "prod")
    assert hashes[3][3] == _encode_and_hash("yg")
    assert hashes[3][4] == _encode_and_hash("ygi")
    assert hashes[3][5] == _encode_and_hash("ygid")
    assert hashes[3][6] == _encode_and_hash("ygido")


def test_get_character_combination_hashes_good_case_no_prefixes(en_tokenizer):
    doc = en_tokenizer("spaCy✨ and Prodigy")
    hashes = get_character_combination_hashes(
        doc=doc,
        case_sensitive=False,
        p_lengths=bytes(),
        s_lengths=bytes(
            (
                2,
                3,
                4,
                5,
            )
        ),
    )

    assert hashes[0][0] == _encode_and_hash("yc")
    assert hashes[0][1] == _encode_and_hash("yca")
    assert hashes[0][2] == _encode_and_hash("ycap")
    assert hashes[0][3] == _encode_and_hash("ycaps")
    assert hashes[1][0] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][1] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][2] == _encode_and_hash("✨", reverse=True)
    assert hashes[1][3] == _encode_and_hash("✨", reverse=True)
    assert hashes[2][0] == _encode_and_hash("dn")
    assert hashes[2][1] == _encode_and_hash("dna")
    assert hashes[2][2] == _encode_and_hash("dna")
    assert hashes[2][3] == _encode_and_hash("dna")
    assert hashes[3][0] == _encode_and_hash("yg")
    assert hashes[3][1] == _encode_and_hash("ygi")
    assert hashes[3][2] == _encode_and_hash("ygid")
    assert hashes[3][3] == _encode_and_hash("ygido")


def test_get_character_combination_hashes_loop_through_lengths(en_tokenizer):
    doc = en_tokenizer("sp𐌞Cé")

    for p_length in range(1, 8):
        for s_length in range(1, 8):

            hashes = get_character_combination_hashes(
                doc=doc,
                case_sensitive=False,
                p_lengths=bytes((p_length,)),
                s_lengths=bytes((s_length,)),
            )

            assert hashes[0][0] == _encode_and_hash("sp𐌞cé"[:p_length])
            assert hashes[0][1] == _encode_and_hash("sp𐌞cé"[-s_length:], reverse=True)


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_character_combination_hashes_turkish_i_with_dot(
    en_tokenizer, case_sensitive
):
    doc = en_tokenizer("İ".lower() + "İ")
    hashes = get_character_combination_hashes(
        doc=doc,
        case_sensitive=case_sensitive,
        p_lengths=bytes(
            (
                1,
                2,
                3,
                4,
            )
        ),
        s_lengths=bytes(
            (
                1,
                2,
                3,
                4,
            )
        ),
    )

    COMBINING_DOT_ABOVE = b"\xcc\x87".decode("UTF-8")
    assert hashes[0][0] == _encode_and_hash("i")
    assert hashes[0][1] == _encode_and_hash("İ".lower())
    if case_sensitive:
        assert hashes[0][2] == _encode_and_hash("İ".lower() + "İ")
        assert hashes[0][3] == _encode_and_hash("İ".lower() + "İ")
        assert hashes[0][4] == _encode_and_hash("İ", reverse=True)
        assert hashes[0][5] == _encode_and_hash(COMBINING_DOT_ABOVE + "İ", reverse=True)
        assert hashes[0][6] == _encode_and_hash("İ".lower() + "İ", reverse=True)
        assert hashes[0][7] == _encode_and_hash("İ".lower() + "İ", reverse=True)

    else:
        assert hashes[0][2] == _encode_and_hash("İ".lower() + "i")
        assert hashes[0][3] == _encode_and_hash("İ".lower() * 2)
        assert hashes[0][4] == _encode_and_hash(COMBINING_DOT_ABOVE, reverse=True)
        assert hashes[0][5] == _encode_and_hash("İ".lower(), reverse=True)
        assert hashes[0][6] == _encode_and_hash(
            COMBINING_DOT_ABOVE + "İ".lower(), reverse=True
        )
        assert hashes[0][7] == _encode_and_hash("İ".lower() * 2, reverse=True)


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_character_combination_hashes_string_store_spec_cases(
    en_tokenizer, case_sensitive
):
    symbol = "FLAG19"
    short_word = "bee"
    normal_word = "serendipity"
    long_word = "serendipity" * 50
    assert len(long_word) > 255
    doc = en_tokenizer(" ".join((symbol, short_word, normal_word, long_word)))
    assert len(doc) == 4
    hashes = get_character_combination_hashes(
        doc=doc,
        case_sensitive=case_sensitive,
        p_lengths=bytes((2,)),
        s_lengths=bytes((2,)),
    )
    assert hashes[0][0] == _encode_and_hash("FL" if case_sensitive else "fl")
    assert hashes[0][1] == _encode_and_hash("91")
    assert hashes[1][0] == _encode_and_hash("be")
    assert hashes[1][1] == _encode_and_hash("ee")
    assert hashes[2][0] == hashes[3][0] == _encode_and_hash("se")
    assert hashes[2][1] == hashes[3][1] == _encode_and_hash("yt")


def test_character_combination_hashes_empty_lengths(en_tokenizer):
    doc = en_tokenizer("and𐌞")
    assert get_character_combination_hashes(
        doc=doc,
        case_sensitive=True,
        p_lengths=bytes(),
        s_lengths=bytes(),
    ).shape == (1, 0)
