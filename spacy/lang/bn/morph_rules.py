# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA


MORPH_RULES = {
    "PRP":  {
        'ঐ':         {LEMMA: PRON_LEMMA, 'PronType': 'Dem'},
        'আমাকে':     {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Person': 'One', 'PronType': 'Prs', 'Case': 'Acc'},
        'কি':        {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Gender': 'Neut', 'PronType': 'Int', 'Case': 'Acc'},
        'সে':        {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Person': 'Three', 'PronType': 'Prs', 'Case': 'Nom'},
        'কিসে':      {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Gender': 'Neut', 'PronType': 'Int', 'Case': 'Acc'},
        'তাকে':      {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Person': 'Three', 'PronType': 'Prs', 'Case': 'Acc'},
        'স্বয়ং':     {LEMMA: PRON_LEMMA, 'Reflex': 'Yes', 'PronType': 'Ref'},
        'কোনগুলো':   {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Gender': 'Neut', 'PronType': 'Int', 'Case': 'Acc'},
        'তুমি':      {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Person': 'Two', 'PronType': 'Prs', 'Case': 'Nom'},
        'তুই':      {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Person': 'Two', 'PronType': 'Prs', 'Case': 'Nom'},
        'তাদেরকে':   {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Person': 'Three', 'PronType': 'Prs', 'Case': 'Acc'},
        'আমরা':      {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Person': 'One ', 'PronType': 'Prs', 'Case': 'Nom'},
        'যিনি':      {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'PronType': 'Rel', 'Case': 'Nom'},
        'আমাদেরকে':  {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Person': 'One', 'PronType': 'Prs', 'Case': 'Acc'},
        'কোন':       {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'PronType': 'Int', 'Case': 'Acc'},
        'কারা':      {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'PronType': 'Int', 'Case': 'Acc'},
        'তোমাকে':    {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Person': 'Two', 'PronType': 'Prs', 'Case': 'Acc'},
        'তোকে':    {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Person': 'Two', 'PronType': 'Prs', 'Case': 'Acc'},
        'খোদ':       {LEMMA: PRON_LEMMA, 'Reflex': 'Yes', 'PronType': 'Ref'},
        'কে':        {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'PronType': 'Int', 'Case': 'Acc'},
        'যারা':      {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'PronType': 'Rel', 'Case': 'Nom'},
        'যে':        {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'PronType': 'Rel', 'Case': 'Nom'},
        'তোমরা':     {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Person': 'Two', 'PronType': 'Prs', 'Case': 'Nom'},
        'তোরা':     {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Person': 'Two', 'PronType': 'Prs', 'Case': 'Nom'},
        'তোমাদেরকে': {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Person': 'Two', 'PronType': 'Prs', 'Case': 'Acc'},
        'তোদেরকে': {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Person': 'Two', 'PronType': 'Prs', 'Case': 'Acc'},
        'আপন':       {LEMMA: PRON_LEMMA, 'Reflex': 'Yes', 'PronType': 'Ref'},
        'এ':         {LEMMA: PRON_LEMMA, 'PronType': 'Dem'},
        'নিজ':       {LEMMA: PRON_LEMMA, 'Reflex': 'Yes', 'PronType': 'Ref'},
        'কার':       {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'PronType': 'Int', 'Case': 'Acc'},
        'যা':        {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Gender': 'Neut', 'PronType': 'Rel', 'Case': 'Nom'},
        'তারা':      {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'Person': 'Three', 'PronType': 'Prs', 'Case': 'Nom'},
        'আমি':       {LEMMA: PRON_LEMMA, 'Number': 'Sing', 'Person': 'One', 'PronType': 'Prs', 'Case': 'Nom'}
    },
    "PRP$": {

        'আমার':    {LEMMA:  PRON_LEMMA, 'Number': 'Sing', 'Person': 'One', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'মোর':     {LEMMA:  PRON_LEMMA, 'Number': 'Sing', 'Person': 'One', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'মোদের':   {LEMMA:  PRON_LEMMA, 'Number': 'Plur', 'Person': 'One', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'তার':     {LEMMA:  PRON_LEMMA, 'Number': 'Sing', 'Person': 'Three', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'তোমাদের': {LEMMA:  PRON_LEMMA, 'Number': 'Plur', 'Person': 'Two', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'আমাদের':  {LEMMA:  PRON_LEMMA, 'Number': 'Plur', 'Person': 'One', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'তোমার':   {LEMMA:  PRON_LEMMA, 'Number': 'Sing', 'Person': 'Two', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'তোর':     {LEMMA:  PRON_LEMMA, 'Number': 'Sing', 'Person': 'Two', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'তাদের':   {LEMMA:  PRON_LEMMA, 'Number': 'Plur', 'Person': 'Three', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'কাদের':   {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'PronType': 'Int', 'Case': 'Acc'},
        'তোদের':   {LEMMA:  PRON_LEMMA, 'Number': 'Plur', 'Person': 'Two', 'PronType': 'Prs', 'Poss': 'Yes',
                    'Case': 'Nom'},
        'যাদের':   {LEMMA: PRON_LEMMA, 'Number': 'Plur', 'PronType': 'Int', 'Case': 'Acc'},
    }
}
