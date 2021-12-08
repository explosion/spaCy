import pytest
import deplacy
from wasabi.util import supports_ansi
from spacy.visualization import AttributeFormat, Visualizer
from spacy.tokens import Span, Doc, Token


SUPPORTS_ANSI = supports_ansi()


def test_visualization_dependency_tree_basic(en_vocab):
    """Test basic dependency tree display."""
    doc = Doc(
        en_vocab,
        words=[
            "The",
            "big",
            "dog",
            "chased",
            "the",
            "frightened",
            "cat",
            "mercilessly",
            ".",
        ],
        heads=[2, 2, 3, None, 6, 6, 3, 3, 3],
        deps=["dep"] * 9,
    )
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], True)
    assert dep_tree == [
        "<╗  ",
        "<╣  ",
        "═╝<╗",
        "═══╣",
        "<╗ ║",
        "<╣ ║",
        "═╝<╣",
        "<══╣",
        "<══╝",
    ]
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], False)
    assert dep_tree == [
        "  ╔>",
        "  ╠>",
        "╔>╚═",
        "╠═══",
        "║ ╔>",
        "║ ╠>",
        "╠>╚═",
        "╠══>",
        "╚══>",
    ]


def test_visualization_dependency_tree_non_initial_sentence(en_vocab):
    """Test basic dependency tree display."""
    doc = Doc(
        en_vocab,
        words=[
            "Something",
            "happened",
            ".",
            "The",
            "big",
            "dog",
            "chased",
            "the",
            "frightened",
            "cat",
            "mercilessly",
            ".",
        ],
        heads=[0, None, 0, 5, 5, 6, None, 9, 9, 6, 6, 6],
        deps=["dep"] * 12,
    )
    dep_tree = Visualizer.render_dependency_tree(doc[3 : len(doc)], True)
    assert dep_tree == [
        "<╗  ",
        "<╣  ",
        "═╝<╗",
        "═══╣",
        "<╗ ║",
        "<╣ ║",
        "═╝<╣",
        "<══╣",
        "<══╝",
    ]
    dep_tree = Visualizer.render_dependency_tree(doc[3 : len(doc)], False)
    assert dep_tree == [
        "  ╔>",
        "  ╠>",
        "╔>╚═",
        "╠═══",
        "║ ╔>",
        "║ ╠>",
        "╠>╚═",
        "╠══>",
        "╚══>",
    ]


def test_visualization_dependency_tree_non_projective(en_vocab):
    """Test dependency tree display with a non-projective dependency."""
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], True)
    assert dep_tree == [
        "<╗    ",
        "═╩═══╗",
        "<╗   ║",
        "═╩═╗<╣",
        "<══║═╣",
        "<╗ ║ ║",
        "<╣ ║ ║",
        "═╝<╝ ║",
        "<════╝",
    ]
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], False)
    assert dep_tree == [
        "    ╔>",
        "╔═══╩═",
        "║   ╔>",
        "╠>╔═╩═",
        "╠═║══>",
        "║ ║ ╔>",
        "║ ║ ╠>",
        "║ ╚>╚═",
        "╚════>",
    ]


def test_visualization_dependency_tree_input_not_span(en_vocab):
    """Test dependency tree display behaviour when the input is not a Span."""
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )

    with pytest.raises(AssertionError):
        Visualizer.render_dependency_tree(doc[1:3], True)


def test_visualization_dependency_tree_highly_nonprojective(en_vocab):
    """Test a highly non-projective tree (colloquial Polish)."""
    doc = Doc(
        en_vocab,
        words=[
            "Owczarki",
            "przecież",
            "niemieckie",
            "zawsze",
            "wierne",
            "są",
            "bardzo",
            ".",
        ],
        heads=[5, 5, 0, 5, 5, None, 4, 5],
        deps=["dep"] * 8,
    )
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], True)
    assert dep_tree == [
        "═╗<╗",
        " ║<╣",
        "<╝ ║",
        "<══╣",
        "═╗<╣",
        "═══╣",
        "<╝ ║",
        "<══╝",
    ]
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], False)
    assert dep_tree == [
        "╔>╔═",
        "╠>║ ",
        "║ ╚>",
        "╠══>",
        "╠>╔═",
        "╠═══",
        "║ ╚>",
        "╚══>",
    ]


def test_visualization_render_native_attribute_int(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )
    assert AttributeFormat("head.i").render(doc[2]) == "3"


def test_visualization_render_native_attribute_str(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )

    assert AttributeFormat("dep_").render(doc[2]) == "dep"


def test_visualization_render_colors(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )

    assert (
        AttributeFormat(
            "dep_",
            value_dependent_fg_colors={"dep": 2},
            value_dependent_bg_colors={"dep": 11},
        ).render(doc[2])
        == "\x1b[38;5;2;48;5;11mdep\x1b[0m"
        if supports_ansi
        else "dep"
    )


def test_visualization_render_colors_only_fg(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )

    assert (
        AttributeFormat(
            "dep_",
            value_dependent_fg_colors={"dep": 2},
        ).render(doc[2])
        == "\x1b[38;5;2mdep\x1b[0m"
        if supports_ansi
        else "dep"
    )


def test_visualization_render_entity_colors_only_bg(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )

    assert (
        AttributeFormat(
            "dep_",
            value_dependent_bg_colors={"dep": 11},
        ).render(doc[2])
        == "\x1b[48;5;11mdep\x1b[0m"
        if supports_ansi
        else "dep"
    )


def test_visualization_render_native_attribute_missing(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )
    with pytest.raises(AttributeError):
        AttributeFormat("depp").render(doc[2])


def test_visualization_render_custom_attribute_str(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )
    Token.set_extension("test", default="tested", force=True)
    assert AttributeFormat("_.test").render(doc[2]) == "tested"


def test_visualization_render_nested_custom_attribute_str(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )

    class Test:
        def __init__(self):
            self.inner_test = "tested"

    Token.set_extension("test", default=Test(), force=True)
    assert AttributeFormat("_.test.inner_test").render(doc[2]) == "tested"


def test_visualization_render_custom_attribute_missing(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )
    with pytest.raises(AttributeError):
        AttributeFormat("._depp").render(doc[2])


def test_visualization_render_permitted_values(en_vocab):
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )
    attribute_format = AttributeFormat("head.i", permitted_values=(3, 7))
    assert [attribute_format.render(token) for token in doc] == [
        "",
        "",
        "3",
        "",
        "",
        "7",
        "7",
        "3",
        "",
    ]


def test_visualization_minimal_render_table_one_sentence(
    fully_featured_doc_one_sentence,
):
    formats = [
        AttributeFormat("tree_left"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_"),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_"),
    ]
    assert (
        Visualizer().render_table(fully_featured_doc_one_sentence, formats).strip()
        == """
  ╔>╔═   poss       Sarah     sarah     PROPN   NNP   NounType=prop|Number=sing   PERSON
  ║ ╚>   case       's        's        PART    POS   Poss=yes                          
╔>╚═══   nsubj      sister    sister    NOUN    NN    Number=sing                       
╠═════   ROOT       flew      fly       VERB    VBD   Tense=past|VerbForm=fin           
╠>╔═══   prep       to        to        ADP     IN                                      
║ ║ ╔>   compound   Silicon   silicon   PROPN   NNP   NounType=prop|Number=sing   GPE   
║ ╚>╚═   pobj       Valley    valley    PROPN   NNP   NounType=prop|Number=sing   GPE   
╠══>╔═   prep       via       via       ADP     IN                                      
║   ╚>   pobj       London    london    PROPN   NNP   NounType=prop|Number=sing   GPE   
╚════>   punct      .         .         PUNCT   .     PunctType=peri
    """.strip()
    )


def test_visualization_minimal_render_table_permitted_values(
    fully_featured_doc_one_sentence,
):
    formats = [
        AttributeFormat("tree_left"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_", permitted_values=("fly", "to")),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_"),
    ]
    assert (
        Visualizer().render_table(fully_featured_doc_one_sentence, formats).strip()
        == """
  ╔>╔═   poss       Sarah           PROPN   NNP   NounType=prop|Number=sing   PERSON
  ║ ╚>   case       's              PART    POS   Poss=yes                          
╔>╚═══   nsubj      sister          NOUN    NN    Number=sing                       
╠═════   ROOT       flew      fly   VERB    VBD   Tense=past|VerbForm=fin           
╠>╔═══   prep       to        to    ADP     IN                                      
║ ║ ╔>   compound   Silicon         PROPN   NNP   NounType=prop|Number=sing   GPE   
║ ╚>╚═   pobj       Valley          PROPN   NNP   NounType=prop|Number=sing   GPE   
╠══>╔═   prep       via             ADP     IN                                      
║   ╚>   pobj       London          PROPN   NNP   NounType=prop|Number=sing   GPE   
╚════>   punct      .               PUNCT   .     PunctType=peri
    """.strip()
    )


def test_visualization_spacing(
    fully_featured_doc_one_sentence,
):
    formats = [
        AttributeFormat("tree_left"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_"),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_"),
    ]
    assert (
        Visualizer()
        .render_table(fully_featured_doc_one_sentence, formats, spacing=1)
        .strip()
        == """
  ╔>╔═ poss     Sarah   sarah   PROPN NNP NounType=prop|Number=sing PERSON
  ║ ╚> case     's      's      PART  POS Poss=yes                        
╔>╚═══ nsubj    sister  sister  NOUN  NN  Number=sing                     
╠═════ ROOT     flew    fly     VERB  VBD Tense=past|VerbForm=fin         
╠>╔═══ prep     to      to      ADP   IN                                  
║ ║ ╔> compound Silicon silicon PROPN NNP NounType=prop|Number=sing GPE   
║ ╚>╚═ pobj     Valley  valley  PROPN NNP NounType=prop|Number=sing GPE   
╠══>╔═ prep     via     via     ADP   IN                                  
║   ╚> pobj     London  london  PROPN NNP NounType=prop|Number=sing GPE   
╚════> punct    .       .       PUNCT .   PunctType=peri
    """.strip()
    )


def test_visualization_minimal_render_table_two_sentences(
    fully_featured_doc_two_sentences,
):
    formats = [
        AttributeFormat("tree_left"),
        AttributeFormat("dep_"),
        AttributeFormat("text"),
        AttributeFormat("lemma_"),
        AttributeFormat("pos_"),
        AttributeFormat("tag_"),
        AttributeFormat("morph"),
        AttributeFormat("ent_type_"),
    ]

    assert (
        Visualizer().render_table(fully_featured_doc_two_sentences, formats).strip()
        == """
  ╔>╔═   poss       Sarah     sarah     PROPN   NNP   NounType=prop|Number=sing   PERSON
  ║ ╚>   case       's        's        PART    POS   Poss=yes                          
╔>╚═══   nsubj      sister    sister    NOUN    NN    Number=sing                       
╠═════   ROOT       flew      fly       VERB    VBD   Tense=past|VerbForm=fin           
╠>╔═══   prep       to        to        ADP     IN                                      
║ ║ ╔>   compound   Silicon   silicon   PROPN   NNP   NounType=prop|Number=sing   GPE   
║ ╚>╚═   pobj       Valley    valley    PROPN   NNP   NounType=prop|Number=sing   GPE   
╠══>╔═   prep       via       via       ADP     IN                                      
║   ╚>   pobj       London    london    PROPN   NNP   NounType=prop|Number=sing   GPE   
╚════>   punct      .         .         PUNCT   .     PunctType=peri                    


╔>   nsubj   She     she    PRON    PRP   Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs    
╠═   ROOT    loved   love   VERB    VBD   Tense=Past|VerbForm=Fin                                  
╠>   dobj    it      it     PRON    PRP   Case=Acc|Gender=Neut|Number=Sing|Person=3|PronType=Prs   
╚>   punct   .       .      PUNCT   .     PunctType=peri    
""".strip()
    )


def test_visualization_rich_render_table_one_sentence(
    fully_featured_doc_one_sentence,
):
    formats = [
        AttributeFormat("tree_left", name="tree", aligns="r", fg_color=2),
        AttributeFormat("dep_", name="dep", fg_color=2),
        AttributeFormat("i", name="index", aligns="r"),
        AttributeFormat("text", name="text"),
        AttributeFormat("lemma_", name="lemma"),
        AttributeFormat("pos_", name="pos", fg_color=100),
        AttributeFormat("tag_", name="tag", fg_color=100),
        AttributeFormat("morph", name="morph", fg_color=100, max_width=15),
        AttributeFormat(
            "ent_type_",
            name="ent",
            fg_color=196,
            value_dependent_fg_colors={"PERSON": 50},
            value_dependent_bg_colors={"PERSON": 12},
        ),
    ]
    assert (
        Visualizer().render_table(fully_featured_doc_one_sentence, formats)
        == "\n\x1b[38;5;2m  tree\x1b[0m   \x1b[38;5;2mdep     \x1b[0m   index   text      lemma     \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   \x1b[38;5;196ment   \x1b[0m\n\x1b[38;5;2m------\x1b[0m   \x1b[38;5;2m--------\x1b[0m   -----   -------   -------   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   \x1b[38;5;196m------\x1b[0m\n\x1b[38;5;2m  ╔>╔═\x1b[0m   \x1b[38;5;2mposs    \x1b[0m       0   Sarah     sarah     \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196m\x1b[38;5;50;48;5;12mPERSON\x1b[0m\x1b[0m\n\x1b[38;5;2m  ║ ╚>\x1b[0m   \x1b[38;5;2mcase    \x1b[0m       1   's        's        \x1b[38;5;100mPART \x1b[0m   \x1b[38;5;100mPOS\x1b[0m   \x1b[38;5;100mPoss=yes       \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╔>╚═══\x1b[0m   \x1b[38;5;2mnsubj   \x1b[0m       2   sister    sister    \x1b[38;5;100mNOUN \x1b[0m   \x1b[38;5;100mNN \x1b[0m   \x1b[38;5;100mNumber=sing    \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠═════\x1b[0m   \x1b[38;5;2mROOT    \x1b[0m       3   flew      fly       \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=past|Verb\x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠>╔═══\x1b[0m   \x1b[38;5;2mprep    \x1b[0m       4   to        to        \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║ ║ ╔>\x1b[0m   \x1b[38;5;2mcompound\x1b[0m       5   Silicon   silicon   \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m║ ╚>╚═\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m       6   Valley    valley    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╠══>╔═\x1b[0m   \x1b[38;5;2mprep    \x1b[0m       7   via       via       \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║   ╚>\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m       8   London    london    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╚════>\x1b[0m   \x1b[38;5;2mpunct   \x1b[0m       9   .         .         \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\n"
        if supports_ansi
        else "\n  tree   dep        index   text      lemma     pos     tag   morph                       ent   \n------   --------   -----   -------   -------   -----   ---   -------------------------   ------\n  ╔>╔═   poss           0   Sarah     sarah     PROPN   NNP   NounType=prop|Number=sing   PERSON\n  ║ ╚>   case           1   's        's        PART    POS   Poss=yes                          \n╔>╚═══   nsubj          2   sister    sister    NOUN    NN    Number=sing                       \n╠═════   ROOT           3   flew      fly       VERB    VBD   Tense=past|VerbForm=fin           \n╠>╔═══   prep           4   to        to        ADP     IN                                      \n║ ║ ╔>   compound       5   Silicon   silicon   PROPN   NNP   NounType=prop|Number=sing   GPE   \n║ ╚>╚═   pobj           6   Valley    valley    PROPN   NNP   NounType=prop|Number=sing   GPE   \n╠══>╔═   prep           7   via       via       ADP     IN                                      \n║   ╚>   pobj           8   London    london    PROPN   NNP   NounType=prop|Number=sing   GPE   \n╚════>   punct          9   .         .         PUNCT   .     PunctType=peri                    \n\n"
    )


def test_visualization_rich_render_table_two_sentences(
    fully_featured_doc_two_sentences,
):
    formats = [
        AttributeFormat("tree_left", name="tree", aligns="r", fg_color=2),
        AttributeFormat("dep_", name="dep", fg_color=2),
        AttributeFormat("i", name="index", aligns="r"),
        AttributeFormat("text", name="text"),
        AttributeFormat("lemma_", name="lemma"),
        AttributeFormat("pos_", name="pos", fg_color=100),
        AttributeFormat("tag_", name="tag", fg_color=100),
        AttributeFormat("morph", name="morph", fg_color=100, max_width=15),
        AttributeFormat(
            "ent_type_",
            name="ent",
            fg_color=196,
            value_dependent_fg_colors={"PERSON": 50},
            value_dependent_bg_colors={"PERSON": 12},
        ),
    ]
    assert (
        Visualizer().render_table(fully_featured_doc_two_sentences, formats)
        == "\n\x1b[38;5;2m  tree\x1b[0m   \x1b[38;5;2mdep     \x1b[0m   index   text      lemma     \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   \x1b[38;5;196ment   \x1b[0m\n\x1b[38;5;2m------\x1b[0m   \x1b[38;5;2m--------\x1b[0m   -----   -------   -------   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   \x1b[38;5;196m------\x1b[0m\n\x1b[38;5;2m  ╔>╔═\x1b[0m   \x1b[38;5;2mposs    \x1b[0m       0   Sarah     sarah     \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196m\x1b[38;5;50;48;5;12mPERSON\x1b[0m\x1b[0m\n\x1b[38;5;2m  ║ ╚>\x1b[0m   \x1b[38;5;2mcase    \x1b[0m       1   's        's        \x1b[38;5;100mPART \x1b[0m   \x1b[38;5;100mPOS\x1b[0m   \x1b[38;5;100mPoss=yes       \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╔>╚═══\x1b[0m   \x1b[38;5;2mnsubj   \x1b[0m       2   sister    sister    \x1b[38;5;100mNOUN \x1b[0m   \x1b[38;5;100mNN \x1b[0m   \x1b[38;5;100mNumber=sing    \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠═════\x1b[0m   \x1b[38;5;2mROOT    \x1b[0m       3   flew      fly       \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=past|Verb\x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m╠>╔═══\x1b[0m   \x1b[38;5;2mprep    \x1b[0m       4   to        to        \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║ ║ ╔>\x1b[0m   \x1b[38;5;2mcompound\x1b[0m       5   Silicon   silicon   \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m║ ╚>╚═\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m       6   Valley    valley    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╠══>╔═\x1b[0m   \x1b[38;5;2mprep    \x1b[0m       7   via       via       \x1b[38;5;100mADP  \x1b[0m   \x1b[38;5;100mIN \x1b[0m   \x1b[38;5;100m               \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\x1b[38;5;2m║   ╚>\x1b[0m   \x1b[38;5;2mpobj    \x1b[0m       8   London    london    \x1b[38;5;100mPROPN\x1b[0m   \x1b[38;5;100mNNP\x1b[0m   \x1b[38;5;100mNounType=prop|N\x1b[0m   \x1b[38;5;196mGPE   \x1b[0m\n\x1b[38;5;2m╚════>\x1b[0m   \x1b[38;5;2mpunct   \x1b[0m       9   .         .         \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m   \x1b[38;5;196m      \x1b[0m\n\n\n\x1b[38;5;2mtree\x1b[0m   \x1b[38;5;2mdep  \x1b[0m   index   text    lemma   \x1b[38;5;100mpos  \x1b[0m   \x1b[38;5;100mtag\x1b[0m   \x1b[38;5;100mmorph          \x1b[0m   \x1b[38;5;196ment\x1b[0m\n\x1b[38;5;2m----\x1b[0m   \x1b[38;5;2m-----\x1b[0m   -----   -----   -----   \x1b[38;5;100m-----\x1b[0m   \x1b[38;5;100m---\x1b[0m   \x1b[38;5;100m---------------\x1b[0m   \x1b[38;5;196m---\x1b[0m\n\x1b[38;5;2m  ╔>\x1b[0m   \x1b[38;5;2mnsubj\x1b[0m      10   She     she     \x1b[38;5;100mPRON \x1b[0m   \x1b[38;5;100mPRP\x1b[0m   \x1b[38;5;100mCase=Nom|Gender\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╠═\x1b[0m   \x1b[38;5;2mROOT \x1b[0m      11   loved   love    \x1b[38;5;100mVERB \x1b[0m   \x1b[38;5;100mVBD\x1b[0m   \x1b[38;5;100mTense=Past|Verb\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╠>\x1b[0m   \x1b[38;5;2mdobj \x1b[0m      12   it      it      \x1b[38;5;100mPRON \x1b[0m   \x1b[38;5;100mPRP\x1b[0m   \x1b[38;5;100mCase=Acc|Gender\x1b[0m   \x1b[38;5;196m   \x1b[0m\n\x1b[38;5;2m  ╚>\x1b[0m   \x1b[38;5;2mpunct\x1b[0m      13   .       .       \x1b[38;5;100mPUNCT\x1b[0m   \x1b[38;5;100m.  \x1b[0m   \x1b[38;5;100mPunctType=peri \x1b[0m   \x1b[38;5;196m   \x1b[0m\n\n"
        if supports_ansi
        else "\n  tree   dep        index   text      lemma     pos     tag   morph                       ent   \n------   --------   -----   -------   -------   -----   ---   -------------------------   ------\n  ╔>╔═   poss           0   Sarah     sarah     PROPN   NNP   NounType=prop|Number=sing   PERSON\n  ║ ╚>   case           1   's        's        PART    POS   Poss=yes                          \n╔>╚═══   nsubj          2   sister    sister    NOUN    NN    Number=sing                       \n╠═════   ROOT           3   flew      fly       VERB    VBD   Tense=past|VerbForm=fin           \n╠>╔═══   prep           4   to        to        ADP     IN                                      \n║ ║ ╔>   compound       5   Silicon   silicon   PROPN   NNP   NounType=prop|Number=sing   GPE   \n║ ╚>╚═   pobj           6   Valley    valley    PROPN   NNP   NounType=prop|Number=sing   GPE   \n╠══>╔═   prep           7   via       via       ADP     IN                                      \n║   ╚>   pobj           8   London    london    PROPN   NNP   NounType=prop|Number=sing   GPE   \n╚════>   punct          9   .         .         PUNCT   .     PunctType=peri                    \n\n\ntree   dep     index   text    lemma   pos     tag   morph                                                    ent\n----   -----   -----   -----   -----   -----   ---   ------------------------------------------------------   ---\n  ╔>   nsubj      10   She     she     PRON    PRP   Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs       \n  ╠═   ROOT       11   loved   love    VERB    VBD   Tense=Past|VerbForm=Fin                                     \n  ╠>   dobj       12   it      it      PRON    PRP   Case=Acc|Gender=Neut|Number=Sing|Person=3|PronType=Prs      \n  ╚>   punct      13   .       .       PUNCT   .     PunctType=peri                                              \n\n"
    )

def test_render_text_with_text_format(
    fully_featured_doc_two_sentences,
):
    formats = [
        AttributeFormat(
            "ent_type_",
            fg_color=50,
            value_dependent_fg_colors={"PERSON": 50},
            value_dependent_bg_colors={"PERSON": 12},
        ),
        AttributeFormat(
            "text",
            fg_color=50,
            bg_color=53,
            value_dependent_fg_colors={"PERSON": 50},
            value_dependent_bg_colors={"PERSON": 12},
        ),
        AttributeFormat(
            "lemma_",
            fg_color=50,
            bg_color=53,
            permitted_values=("fly", "valley")
        ),
    ]
    assert Visualizer().render_text(fully_featured_doc_two_sentences, formats) == "\x1b[38;5;50;48;5;53mSarah\x1b[0m \x1b[38;5;50;48;5;12mPERSON\x1b[0m's sister \x1b[38;5;50;48;5;53mflew\x1b[0m \x1b[38;5;50;48;5;53mfly\x1b[0m to \x1b[38;5;50;48;5;53mSilicon\x1b[0m \x1b[38;5;50mGPE\x1b[0m \x1b[38;5;50;48;5;53mValley\x1b[0m \x1b[38;5;50mGPE\x1b[0m \x1b[38;5;50;48;5;53mvalley\x1b[0m via \x1b[38;5;50;48;5;53mLondon\x1b[0m \x1b[38;5;50mGPE\x1b[0m. She loved it." if supports_ansi else "Sarah PERSON's sister flew fly to Silicon GPE Valley GPE valley via London GPE. She loved it."

def test_render_text_without_text_format(
    fully_featured_doc_two_sentences,
):
    formats = [
        AttributeFormat(
            "ent_type_",
            value_dependent_fg_colors={"PERSON": 50},
            value_dependent_bg_colors={"PERSON": 12},
        ),
        AttributeFormat(
            "lemma_",
            permitted_values=("fly", "valley")
        ),
    ]
    assert Visualizer().render_text(fully_featured_doc_two_sentences, formats) == "Sarah \x1b[38;5;50;48;5;12mPERSON\x1b[0m's sister flew fly to Silicon GPE Valley GPE valley via London GPE. She loved it." if supports_ansi else "Sarah PERSON's sister flew fly to Silicon GPE Valley GPE valley via London GPE. She loved it."