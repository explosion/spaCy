from .lexeme import lex_of
from .lexeme import sic_of

from .tokens import Tokens

# Don't know how to get the enum Python visible :(

SIC = 0
LEX = 1
NORM = 2
SHAPE = 3
LAST3 = 4

__all__ = [Tokens, lex_of, sic_of, SIC, LEX, NORM, SHAPE, LAST3]


"""
from .tokens import ids_from_string
from .tokens import group_by

from .lex import sic_of
from .lex import lex_of
from .lex import normed_of
from .lex import first_of
from .lex import last_three_of

from .lex import cluster_of
from .lex import prob_of

from .lex import is_oft_upper
from .lex import is_oft_title

from .lex import can_noun
from .lex import can_verb
from .lex import can_adj
from .lex import can_adv
"""
