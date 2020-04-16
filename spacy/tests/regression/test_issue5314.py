from bin.wiki_entity_linking.wikipedia_processor import _process_wp_text

title = "Arkæologi"

text = """<text bytes="11456" xml:space="preserve">[[Fil:Archäologie schichtengrabung.jpg|thumb|Arkæologisk [[udgravning]] med profil.]] '''Arkæologi''' er studiet af tidligere tiders [[menneske]]lige [[aktivitet]], primært gennem studiet af menneskets materielle levn.</text>"""


def test_issue_xxx():
    clean_text, entities = _process_wp_text(title, text, {})
    assert clean_text is not None
