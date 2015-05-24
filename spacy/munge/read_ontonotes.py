import re


docid_re = re.compile(r'<DOCID>([^>]+)</DOCID>')
doctype_re = re.compile(r'<DOCTYPE SOURCE="[^"]+">([^>]+)</DOCTYPE>')
datetime_re = re.compile(r'<DATETIME>([^>]+)</DATETIME>')
headline_re = re.compile(r'<HEADLINE>(.+)</HEADLINE>', re.DOTALL)
post_re = re.compile(r'<POST>(.+)</POST>', re.DOTALL)
poster_re = re.compile(r'<POSTER>(.+)</POSTER>')
postdate_re = re.compile(r'<POSTDATE>(.+)</POSTDATE>')
tag_re = re.compile(r'<[^>]+>[^>]+</[^>]+>')


def sgml_extract(text_data):
    """Extract text from the OntoNotes web documents.

    Format:
    [{
        docid: string,
        doctype: string,
        datetime: string,
        poster: string,
        postdate: string
        text: [string]
    }]
    """
    return {
        'docid': _get_one(docid_re, text_data, required=True),
        'doctype': _get_one(doctype_re, text_data, required=True),
        'datetime': _get_one(datetime_re, text_data, required=True),
        'headline': _get_one(headline_re, text_data, required=True),
        'poster': _get_one(poster_re, _get_one(post_re, text_data)),
        'postdate': _get_one(postdate_re, _get_one(post_re, text_data)),
        'text': _get_text(_get_one(post_re, text_data)).strip()
    }


def _get_one(regex, text, required=False):
    matches = regex.search(text)
    if not matches and not required:
        return ''
    assert len(matches.groups()) == 1, matches
    return matches.groups()[0].strip()


def _get_text(data):
    return tag_re.sub('', data).replace('<P>', '').replace('</P>', '')
