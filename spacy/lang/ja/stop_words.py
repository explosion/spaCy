# coding: utf8
from __future__ import unicode_literals

# This list was created by taking the top 2000 words from a Wikipedia dump and
# filtering out everything that wasn't hiragana. ー (one) was also added.
# Considered keeping some non-hiragana words but too many place names were
# present.
STOP_WORDS = set("""
あ あっ あまり あり ある あるいは あれ
い いい いう いく いずれ いっ いつ いる いわ
うち
え
お おい おけ および おら おり
か かけ かつ かつて かなり から が
き きっかけ
くる くん
こ こう ここ こと この これ ご ごと
さ さらに さん
し しか しかし しまう しまっ しよう
す すぐ すべて する ず
せ せい せる
そう そこ そして その それ それぞれ
た たい ただし たち ため たら たり だ だけ だっ
ち ちゃん
つ つい つけ つつ
て で でき できる です
と とき ところ とっ とも どう
な ない なお なかっ ながら なく なけれ なし なっ など なら なり なる
に にて
ぬ
ね
の のち のみ
は はじめ ば
ひと
ぶり
へ べき
ほか ほとんど ほど ほぼ
ま ます また まで まま
み
も もう もっ もと もの
や やっ
よ よう よく よっ より よる よれ
ら らしい られ られる
る
れ れる
を
ん
一
""".split())
