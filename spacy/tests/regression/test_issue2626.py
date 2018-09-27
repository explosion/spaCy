# coding: utf8
from __future__ import unicode_literals


def test_issue2626(en_tokenizer):
    """Check that sentence doesn't cause an infinite loop in the tokenizer."""
    text = """
    ABLEItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume TABLE ItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume ItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume
    """
    doc = en_tokenizer(text)
