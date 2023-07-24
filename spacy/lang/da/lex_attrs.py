from ...attrs import LIKE_NUM

# Source http://fjern-uv.dk/tal.php
_num_words = """nul
en et to tre fire fem seks syv otte ni ti
elleve tolv tretten fjorten femten seksten sytten atten nitten tyve
enogtyve toogtyve treogtyve fireogtyve femogtyve seksogtyve syvogtyve otteogtyve niogtyve tredive
enogtredive toogtredive treogtredive fireogtredive femogtredive seksogtredive syvogtredive otteogtredive niogtredive fyrre
enogfyrre toogfyrre treogfyrre fireogfyrre femgogfyrre seksogfyrre syvogfyrre otteogfyrre niogfyrre halvtreds
enoghalvtreds tooghalvtreds treoghalvtreds fireoghalvtreds femoghalvtreds seksoghalvtreds syvoghalvtreds otteoghalvtreds nioghalvtreds tres
enogtres toogtres treogtres fireogtres femogtres seksogtres syvogtres otteogtres niogtres halvfjerds
enoghalvfjerds tooghalvfjerds treoghalvfjerds fireoghalvfjerds femoghalvfjerds seksoghalvfjerds syvoghalvfjerds otteoghalvfjerds nioghalvfjerds firs
enogfirs toogfirs treogfirs fireogfirs femogfirs seksogfirs syvogfirs otteogfirs niogfirs halvfems
enoghalvfems tooghalvfems treoghalvfems fireoghalvfems femoghalvfems seksoghalvfems syvoghalvfems otteoghalvfems nioghalvfems hundrede
million milliard billion billiard trillion trilliard
""".split()


# Source: http://www.duda.dk/video/dansk/grammatik/talord/talord.html
_ordinal_words = """nulte
første anden tredje fjerde femte sjette syvende ottende niende tiende
elfte tolvte trettende fjortende femtende sekstende syttende attende nittende tyvende
enogtyvende toogtyvende treogtyvende fireogtyvende femogtyvende seksogtyvende syvogtyvende otteogtyvende niogtyvende tredivte enogtredivte toogtredivte treogtredivte fireogtredivte femogtredivte seksogtredivte syvogtredivte otteogtredivte niogtredivte fyrretyvende
enogfyrretyvende toogfyrretyvende treogfyrretyvende fireogfyrretyvende femogfyrretyvende seksogfyrretyvende syvogfyrretyvende otteogfyrretyvende niogfyrretyvende halvtredsindstyvende enoghalvtredsindstyvende
tooghalvtredsindstyvende treoghalvtredsindstyvende fireoghalvtredsindstyvende femoghalvtredsindstyvende seksoghalvtredsindstyvende syvoghalvtredsindstyvende otteoghalvtredsindstyvende nioghalvtredsindstyvende
tresindstyvende enogtresindstyvende toogtresindstyvende treogtresindstyvende fireogtresindstyvende femogtresindstyvende seksogtresindstyvende syvogtresindstyvende otteogtresindstyvende niogtresindstyvende halvfjerdsindstyvende
enoghalvfjerdsindstyvende tooghalvfjerdsindstyvende treoghalvfjerdsindstyvende fireoghalvfjerdsindstyvende femoghalvfjerdsindstyvende seksoghalvfjerdsindstyvende syvoghalvfjerdsindstyvende otteoghalvfjerdsindstyvende nioghalvfjerdsindstyvende firsindstyvende
enogfirsindstyvende toogfirsindstyvende treogfirsindstyvende fireogfirsindstyvende femogfirsindstyvende seksogfirsindstyvende syvogfirsindstyvende otteogfirsindstyvende niogfirsindstyvende halvfemsindstyvende
enoghalvfemsindstyvende tooghalvfemsindstyvende treoghalvfemsindstyvende fireoghalvfemsindstyvende femoghalvfemsindstyvende seksoghalvfemsindstyvende syvoghalvfemsindstyvende otteoghalvfemsindstyvende nioghalvfemsindstyvende
""".split()


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    if text.lower() in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}
