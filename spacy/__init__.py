from .lexeme import lex_of
from .lexeme import sic_of
from .lexeme import length_of

from .tokens import Tokens

# Don't know how to get the enum Python visible :(

SIC = 0
LEX = 1
NORM = 2
SHAPE = 3
LAST3 = 4
LENGTH = 5

__all__ = [Tokens, lex_of, sic_of, length_of, SIC, LEX, NORM, SHAPE, LAST3, LENGTH]
