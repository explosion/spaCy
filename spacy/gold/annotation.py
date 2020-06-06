class TokenAnnotation:
    def __init__(
        self,
        ids=None,
        words=None,
        tags=None,
        pos=None,
        morphs=None,
        lemmas=None,
        heads=None,
        deps=None,
        entities=None,
        sent_starts=None,
        brackets=None,
    ):
        self.ids = ids if ids else []
        self.words = words if words else []
        self.tags = tags if tags else []
        self.pos = pos if pos else []
        self.morphs = morphs if morphs else []
        self.lemmas = lemmas if lemmas else []
        self.heads = heads if heads else []
        self.deps = deps if deps else []
        self.entities = entities if entities else []
        self.sent_starts = sent_starts if sent_starts else []
        self.brackets_by_start = {}
        if brackets:
            for b_start, b_end, b_label in brackets:
                self.brackets_by_start.setdefault(b_start, []).append((b_end, b_label))

    @property
    def brackets(self):
        brackets = []
        for start, ends_labels in self.brackets_by_start.items():
            for end, label in ends_labels:
                brackets.append((start, end, label))
        return brackets

    @classmethod
    def from_dict(cls, token_dict):
        return cls(
            ids=token_dict.get("ids", None),
            words=token_dict.get("words", None),
            tags=token_dict.get("tags", None),
            pos=token_dict.get("pos", None),
            morphs=token_dict.get("morphs", None),
            lemmas=token_dict.get("lemmas", None),
            heads=token_dict.get("heads", None),
            deps=token_dict.get("deps", None),
            entities=token_dict.get("entities", None),
            sent_starts=token_dict.get("sent_starts", None),
            brackets=token_dict.get("brackets", None),
        )

    def to_dict(self):
        return {
            "ids": self.ids,
            "words": self.words,
            "tags": self.tags,
            "pos": self.pos,
            "morphs": self.morphs,
            "lemmas": self.lemmas,
            "heads": self.heads,
            "deps": self.deps,
            "entities": self.entities,
            "sent_starts": self.sent_starts,
            "brackets": self.brackets,
        }

    def get_id(self, i):
        return self.ids[i] if i < len(self.ids) else i

    def get_word(self, i):
        return self.words[i] if i < len(self.words) else ""

    def get_tag(self, i):
        return self.tags[i] if i < len(self.tags) else "-"

    def get_pos(self, i):
        return self.pos[i] if i < len(self.pos) else ""

    def get_morph(self, i):
        return self.morphs[i] if i < len(self.morphs) else ""

    def get_lemma(self, i):
        return self.lemmas[i] if i < len(self.lemmas) else ""

    def get_head(self, i):
        return self.heads[i] if i < len(self.heads) else i

    def get_dep(self, i):
        return self.deps[i] if i < len(self.deps) else ""

    def get_entity(self, i):
        return self.entities[i] if i < len(self.entities) else "-"

    def get_sent_start(self, i):
        return self.sent_starts[i] if i < len(self.sent_starts) else None

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return self.__str__()


class DocAnnotation:
    def __init__(self, cats=None, links=None):
        self.cats = cats if cats else {}
        self.links = links if links else {}

    @classmethod
    def from_dict(cls, doc_dict):
        return cls(cats=doc_dict.get("cats", None), links=doc_dict.get("links", None))

    def to_dict(self):
        return {"cats": self.cats, "links": self.links}

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return self.__str__()
