# encoding: utf8
# data from Korakot Chaovavanich (https://www.facebook.com/photo.php?fbid=390564854695031&set=p.390564854695031&type=3&permPage=1&ifg=1)
from __future__ import unicode_literals

from ..symbols import *

TAG_MAP = {
    #NOUN
    "NOUN":     {POS: NOUN},
    "NCMN":     {POS: NOUN},
    "NTTL":     {POS: NOUN},
    "CNIT":     {POS: NOUN},
    "CLTV":     {POS: NOUN},
    "CMTR":     {POS: NOUN},
    "CFQC":     {POS: NOUN},
    "CVBL":     {POS: NOUN},
    #PRON
    "PRON":     {POS: PRON},
    "NPRP":     {POS: PRON},
    # ADJ
    "ADJ":      {POS: ADJ},
    "NONM":      {POS: ADJ},
    "VATT":      {POS: ADJ},
    "DONM":      {POS: ADJ},
    # ADV
    "ADV":      {POS: ADV},
    "ADVN":      {POS: ADV},
    "ADVI":      {POS: ADV},
    "ADVP":      {POS: ADV},
    "ADVS":      {POS: ADV},
	# INT
    "INT":      {POS: INTJ},
    # PRON
    "PROPN":    {POS: PROPN},
    "PPRS":    {POS: PROPN},
    "PDMN":    {POS: PROPN},
    "PNTR":    {POS: PROPN},
    # DET
    "DET":      {POS: DET},
    "DDAN":      {POS: DET},
    "DDAC":      {POS: DET},
    "DDBQ":      {POS: DET},
    "DDAQ":      {POS: DET},
    "DIAC":      {POS: DET},
    "DIBQ":      {POS: DET},
    "DIAQ":      {POS: DET},
    "DCNM":      {POS: DET},
    # NUM
    "NUM":      {POS: NUM},
    "NCNM":      {POS: NUM},
    "NLBL":      {POS: NUM},
    "DCNM":      {POS: NUM},
	# AUX
    "AUX":      {POS: AUX},
    "XVBM":      {POS: AUX},
    "XVAM":      {POS: AUX},
    "XVMM":      {POS: AUX},
    "XVBB":      {POS: AUX},
    "XVAE":      {POS: AUX},
	# ADP
    "ADP":      {POS: ADP},
    "RPRE":      {POS: ADP},
    # CCONJ
    "CCONJ":    {POS: CCONJ},
    "JCRG":    {POS: CCONJ},
	# SCONJ
    "SCONJ":    {POS: SCONJ},
    "PREL":    {POS: SCONJ},
    "JSBR":    {POS: SCONJ},
    "JCMP":    {POS: SCONJ},
    # PART
    "PART":    {POS: PART},
    "FIXN":    {POS: PART},
    "FIXV":    {POS: PART},
    "EAFF":    {POS: PART},
    "AITT":    {POS: PART},
    "NEG":    {POS: PART},
    # PUNCT
    "PUNCT":    {POS: PUNCT},
    "PUNC":    {POS: PUNCT}
}