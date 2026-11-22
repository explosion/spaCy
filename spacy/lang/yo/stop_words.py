# stop words as whitespace-separated list.
# Source: https://raw.githubusercontent.com/dohliam/more-stoplists/master/yo/yo.txt
# Single-character fragments (bare combining marks, isolated consonants and
# vowels that do not occur as standalone words) were removed. See #14036.

STOP_WORDS = set(
    "a an bá bí bẹ̀rẹ̀ fún fẹ́ gbogbo inú jù jẹ jẹ́ kan kì kí kò láti lè lọ m mi mo "
    "máa mọ̀ n ni náà ní nígbà nítorí nǹkan o padà pé púpọ̀ pẹ̀lú rẹ̀ sì sí sínú ti "
    "tí wà wá wọn wọ́n yìí àti àwọn á é í ò òun ó ú ń ńlá ǹ ṣe ṣé ṣùgbọ́n ẹ ẹmọ́ ọ "
    "ọjọ́ ọ̀pọ̀lọpọ̀".split()
)