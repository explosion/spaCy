import pytest

from bin.wiki_entity_linking.wikipedia_processor import _process_wp_text

old_format_text = """<text bytes="11456" xml:space="preserve">[[Fil:Archäologie schichtengrabung.jpg|thumb|Arkæologisk [[udgravning]] med profil.]] '''Arkæologi''' er studiet af tidligere tiders [[menneske]]lige [[aktivitet]], primært gennem studiet af menneskets materielle levn.</text>"""
new_format_text = """<text xml:space="preserve">[[Fil:Archäologie schichtengrabung.jpg|thumb|Arkæologisk [[udgravning]] med profil.]] '''Arkæologi''' er studiet af tidligere tiders [[menneske]]lige [[aktivitet]], primært gennem studiet af menneskets materielle levn.</text>"""
potential_future_format = """<text bytes="11456" xml:space="preserve">[[Fil:Archäologie schichtengrabung.jpg|thumb|Arkæologisk [[udgravning]] med profil.]] '''Arkæologi''' er studiet af tidligere tiders [[menneske]]lige [[aktivitet]], primært gennem studiet af menneskets materielle levn.</text>"""


@pytest.mark.parametrize(
    "text", [old_format_text, new_format_text, potential_future_format]
)
def test_issue5314(text):
    title = "Arkæologi"
    clean_text, _ = _process_wp_text(title, text, {})

    expected_text = "Arkæologi er studiet af tidligere tiders menneskelige aktivitet, primært gennem studiet af menneskets materielle levn."
    assert clean_text.strip() == expected_text
