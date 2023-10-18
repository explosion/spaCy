doc_rendering = {
    "text": "Welcome to the Bank of China.",
    "spans": [
        {"start_token": 2, "end_token": 5, "label": "SkillNC"},
        {"start_token": 0, "end_token": 2, "label": "Skill"},
        {"start_token": 1, "end_token": 3, "label": "Skill"},
    ],
    "tokens": ["Welcome", "to", "the", "Bank", "of", "China", "."],
}

from spacy import displacy

html = displacy.render(
    doc_rendering,
    style="span",
    manual=True,
    options={"colors": {"Skill": "#56B4E9", "SkillNC": "#FF5733"}},
)
with open("render.html", "w") as file:
    file.write(html)
