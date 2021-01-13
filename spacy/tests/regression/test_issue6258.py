import pytest
from pydantic import ValidationError
from spacy.schemas import TokenPattern, TokenPatternSchema


def test_issue6258():
    """Test that the non-empty constraint pattern field is respected"""
    # These one is valid
    TokenPatternSchema(pattern=[TokenPattern()])
    # But an empty pattern list should fail to validate
    # based on the schema's constraint
    with pytest.raises(ValidationError):
        TokenPatternSchema(pattern=[])
