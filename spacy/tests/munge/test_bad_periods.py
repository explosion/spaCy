import spacy.munge.read_conll

hongbin_example = """
1       2.      0.      LS      _       24      meta    _       _       _
2       .       .       .       _       1       punct   _       _       _
3       Wang    wang    NNP     _       4       compound        _       _       _
4       Hongbin hongbin NNP     _       16      nsubj   _       _       _
5       ,       ,       ,       _       4       punct   _       _       _
6       the     the     DT      _       11      det     _       _       _
7       "       "       ``      _       11      punct   _       _       _
8       communist       communist       JJ      _       11      amod    _       _       _
9       trail   trail   NN      _       11      compound        _       _       _
10      -       -       HYPH    _       11      punct   _       _       _
11      blazer  blazer  NN      _       4       appos   _       _       _
12      ,       ,       ,       _       16      punct   _       _       _
13      "       "       ''      _       16      punct   _       _       _
14      has     have    VBZ     _       16      aux     _       _       _
15      not     not     RB      _       16      neg     _       _       _
16      turned  turn    VBN     _       24      ccomp   _       _       _
17      into    into    IN      syn=CLR 16      prep    _       _       _
18      a       a       DT      _       19      det     _       _       _
19      capitalist      capitalist      NN      _       17      pobj    _       _       _
20      (       (       -LRB-   _       24      punct   _       _       _
21      he      he      PRP     _       24      nsubj   _       _       _
22      does    do      VBZ     _       24      aux     _       _       _
23      n't     not     RB      _       24      neg     _       _       _
24      have    have    VB      _       0       root    _       _       _
25      any     any     DT      _       26      det     _       _       _
26      shares  share   NNS     _       24      dobj    _       _       _
27      ,       ,       ,       _       24      punct   _       _       _
28      does    do      VBZ     _       30      aux     _       _       _
29      n't     not     RB      _       30      neg     _       _       _
30      have    have    VB      _       24      conj    _       _       _
31      any     any     DT      _       32      det     _       _       _
32      savings saving  NNS     _       30      dobj    _       _       _
33      ,       ,       ,       _       30      punct   _       _       _
34      does    do      VBZ     _       36      aux     _       _       _
35      n't     not     RB      _       36      neg     _       _       _
36      have    have    VB      _       30      conj    _       _       _
37      his     his     PRP$    _       39      poss    _       _       _
38      own     own     JJ      _       39      amod    _       _       _
39      car     car     NN      _       36      dobj    _       _       _
40      ,       ,       ,       _       36      punct   _       _       _
41      and     and     CC      _       36      cc      _       _       _
42      does    do      VBZ     _       44      aux     _       _       _
43      n't     not     RB      _       44      neg     _       _       _
44      have    have    VB      _       36      conj    _       _       _
45      a       a       DT      _       46      det     _       _       _
46      mansion mansion NN      _       44      dobj    _       _       _
47      ;       ;       .       _       24      punct   _       _       _
""".strip()


def test_hongbin():
    words, annot = spacy.munge.read_conll.parse(hongbin_example, strip_bad_periods=True)
    assert words[annot[0]['head']] == 'have'
    assert words[annot[1]['head']] == 'Hongbin'


