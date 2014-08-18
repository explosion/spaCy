from .lexeme import lex_of
from .lexeme import length_of

from .tokens import Tokens

# Don't know how to get the enum Python visible :(

LEX = 0
NORM = 1
SHAPE = 2
LAST3 = 3
LENGTH = 4

__all__ = [Tokens, lex_of, length_of, LEX, NORM, SHAPE, LAST3, LENGTH]
