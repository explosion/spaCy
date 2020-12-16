# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM


_exc = {
    ".ق ": [{LEMMA: "قمری", ORTH: ".ق "}],
    ".م": [{LEMMA: "میلادی", ORTH: ".م"}],
    ".هـ": [{LEMMA: "هجری", ORTH: ".هـ"}],
    "ب.م": [{LEMMA: "بعد از میلاد", ORTH: "ب.م"}],
    "ق.م": [{LEMMA: "قبل از میلاد", ORTH: "ق.م"}],
}

_exc.update(
    {
        "آبرویت": [
            {ORTH: "آبروی", LEMMA: "آبروی", NORM: "آبروی", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "آب‌نباتش": [
            {ORTH: "آب‌نبات", LEMMA: "آب‌نبات", NORM: "آب‌نبات", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "آثارش": [
            {ORTH: "آثار", LEMMA: "آثار", NORM: "آثار", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "آخرش": [
            {ORTH: "آخر", LEMMA: "آخر", NORM: "آخر", TAG: "ADV"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "آدمهاست": [
            {ORTH: "آدمها", LEMMA: "آدمها", NORM: "آدمها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "آرزومندیم": [
            {ORTH: "آرزومند", LEMMA: "آرزومند", NORM: "آرزومند", TAG: "ADJ"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "آزادند": [
            {ORTH: "آزاد", LEMMA: "آزاد", NORM: "آزاد", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "آسیب‌پذیرند": [
            {ORTH: "آسیب‌پذیر", LEMMA: "آسیب‌پذیر", NORM: "آسیب‌پذیر", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "آفریده‌اند": [
            {ORTH: "آفریده‌", LEMMA: "آفریده‌", NORM: "آفریده‌", TAG: "NOUN"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "آمدنش": [
            {ORTH: "آمدن", LEMMA: "آمدن", NORM: "آمدن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "آمریکاست": [
            {ORTH: "آمریکا", LEMMA: "آمریکا", NORM: "آمریکا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "آنجاست": [
            {ORTH: "آنجا", LEMMA: "آنجا", NORM: "آنجا", TAG: "ADV"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "آنست": [
            {ORTH: "آن", LEMMA: "آن", NORM: "آن", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "آنند": [
            {ORTH: "آن", LEMMA: "آن", NORM: "آن", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "آن‌هاست": [
            {ORTH: "آن‌ها", LEMMA: "آن‌ها", NORM: "آن‌ها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "آپاداناست": [
            {ORTH: "آپادانا", LEMMA: "آپادانا", NORM: "آپادانا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "اجتماعی‌مان": [
            {ORTH: "اجتماعی‌", LEMMA: "اجتماعی‌", NORM: "اجتماعی‌", TAG: "ADJ"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "اجدادت": [
            {ORTH: "اجداد", LEMMA: "اجداد", NORM: "اجداد", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "اجدادش": [
            {ORTH: "اجداد", LEMMA: "اجداد", NORM: "اجداد", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اجدادی‌شان": [
            {ORTH: "اجدادی‌", LEMMA: "اجدادی‌", NORM: "اجدادی‌", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "اجراست": [
            {ORTH: "اجرا", LEMMA: "اجرا", NORM: "اجرا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "اختیارش": [
            {ORTH: "اختیار", LEMMA: "اختیار", NORM: "اختیار", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اخلاقشان": [
            {ORTH: "اخلاق", LEMMA: "اخلاق", NORM: "اخلاق", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "ادعایمان": [
            {ORTH: "ادعای", LEMMA: "ادعای", NORM: "ادعای", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "اذیتش": [
            {ORTH: "اذیت", LEMMA: "اذیت", NORM: "اذیت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اراده‌اش": [
            {ORTH: "اراده‌", LEMMA: "اراده‌", NORM: "اراده‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "ارتباطش": [
            {ORTH: "ارتباط", LEMMA: "ارتباط", NORM: "ارتباط", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "ارتباطمان": [
            {ORTH: "ارتباط", LEMMA: "ارتباط", NORM: "ارتباط", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "ارزشهاست": [
            {ORTH: "ارزشها", LEMMA: "ارزشها", NORM: "ارزشها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "ارزی‌اش": [
            {ORTH: "ارزی‌", LEMMA: "ارزی‌", NORM: "ارزی‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "اره‌اش": [
            {ORTH: "اره‌", LEMMA: "اره‌", NORM: "اره‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "ازش": [
            {ORTH: "از", LEMMA: "از", NORM: "از", TAG: "ADP"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "ازین": [
            {ORTH: "از", LEMMA: "از", NORM: "از", TAG: "ADP"},
            {ORTH: "ین", LEMMA: "ین", NORM: "ین", TAG: "NOUN"},
        ],
        "ازین‌هاست": [
            {ORTH: "از", LEMMA: "از", NORM: "از", TAG: "ADP"},
            {ORTH: "ین‌ها", LEMMA: "ین‌ها", NORM: "ین‌ها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "استخوانند": [
            {ORTH: "استخوان", LEMMA: "استخوان", NORM: "استخوان", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "اسلامند": [
            {ORTH: "اسلام", LEMMA: "اسلام", NORM: "اسلام", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "اسلامی‌اند": [
            {ORTH: "اسلامی‌", LEMMA: "اسلامی‌", NORM: "اسلامی‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "اسلحه‌هایشان": [
            {ORTH: "اسلحه‌های", LEMMA: "اسلحه‌های", NORM: "اسلحه‌های", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "اسمت": [
            {ORTH: "اسم", LEMMA: "اسم", NORM: "اسم", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "اسمش": [
            {ORTH: "اسم", LEMMA: "اسم", NORM: "اسم", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اشتباهند": [
            {ORTH: "اشتباه", LEMMA: "اشتباه", NORM: "اشتباه", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "اصلش": [
            {ORTH: "اصل", LEMMA: "اصل", NORM: "اصل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اطاقش": [
            {ORTH: "اطاق", LEMMA: "اطاق", NORM: "اطاق", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اعتقادند": [
            {ORTH: "اعتقاد", LEMMA: "اعتقاد", NORM: "اعتقاد", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "اعلایش": [
            {ORTH: "اعلای", LEMMA: "اعلای", NORM: "اعلای", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "افتراست": [
            {ORTH: "افترا", LEMMA: "افترا", NORM: "افترا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "افطارت": [
            {ORTH: "افطار", LEMMA: "افطار", NORM: "افطار", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "اقوامش": [
            {ORTH: "اقوام", LEMMA: "اقوام", NORM: "اقوام", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "امروزیش": [
            {ORTH: "امروزی", LEMMA: "امروزی", NORM: "امروزی", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اموالش": [
            {ORTH: "اموال", LEMMA: "اموال", NORM: "اموال", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "امیدوارند": [
            {ORTH: "امیدوار", LEMMA: "امیدوار", NORM: "امیدوار", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "امیدواریم": [
            {ORTH: "امیدوار", LEMMA: "امیدوار", NORM: "امیدوار", TAG: "ADJ"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "انتخابهایم": [
            {ORTH: "انتخابها", LEMMA: "انتخابها", NORM: "انتخابها", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "NOUN"},
        ],
        "انتظارم": [
            {ORTH: "انتظار", LEMMA: "انتظار", NORM: "انتظار", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "انجمنم": [
            {ORTH: "انجمن", LEMMA: "انجمن", NORM: "انجمن", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "اندرش": [
            {ORTH: "اندر", LEMMA: "اندر", NORM: "اندر", TAG: "ADP"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "انشایش": [
            {ORTH: "انشای", LEMMA: "انشای", NORM: "انشای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "انگشتشان": [
            {ORTH: "انگشت", LEMMA: "انگشت", NORM: "انگشت", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "انگشتهایش": [
            {ORTH: "انگشتهای", LEMMA: "انگشتهای", NORM: "انگشتهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اهمیتشان": [
            {ORTH: "اهمیت", LEMMA: "اهمیت", NORM: "اهمیت", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "اهمیتند": [
            {ORTH: "اهمیت", LEMMA: "اهمیت", NORM: "اهمیت", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "اوایلش": [
            {ORTH: "اوایل", LEMMA: "اوایل", NORM: "اوایل", TAG: "ADV"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اوست": [
            {ORTH: "او", LEMMA: "او", NORM: "او", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "اولش": [
            {ORTH: "اول", LEMMA: "اول", NORM: "اول", TAG: "ADV"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "اولشان": [
            {ORTH: "اول", LEMMA: "اول", NORM: "اول", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "اولم": [
            {ORTH: "اول", LEMMA: "اول", NORM: "اول", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "اکثرشان": [
            {ORTH: "اکثر", LEMMA: "اکثر", NORM: "اکثر", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "ایتالیاست": [
            {ORTH: "ایتالیا", LEMMA: "ایتالیا", NORM: "ایتالیا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "ایرانی‌اش": [
            {ORTH: "ایرانی‌", LEMMA: "ایرانی‌", NORM: "ایرانی‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "اینجاست": [
            {ORTH: "اینجا", LEMMA: "اینجا", NORM: "اینجا", TAG: "ADV"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "این‌هاست": [
            {ORTH: "این‌ها", LEMMA: "این‌ها", NORM: "این‌ها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "بابات": [
            {ORTH: "بابا", LEMMA: "بابا", NORM: "بابا", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "بارش": [
            {ORTH: "بار", LEMMA: "بار", NORM: "بار", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بازیگرانش": [
            {ORTH: "بازیگران", LEMMA: "بازیگران", NORM: "بازیگران", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بازیگرمان": [
            {ORTH: "بازیگر", LEMMA: "بازیگر", NORM: "بازیگر", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "بازیگرهایم": [
            {ORTH: "بازیگرها", LEMMA: "بازیگرها", NORM: "بازیگرها", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "NOUN"},
        ],
        "بازی‌اش": [
            {ORTH: "بازی‌", LEMMA: "بازی‌", NORM: "بازی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "بالاست": [
            {ORTH: "بالا", LEMMA: "بالا", NORM: "بالا", TAG: "ADV"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "باورند": [
            {ORTH: "باور", LEMMA: "باور", NORM: "باور", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "بجاست": [
            {ORTH: "بجا", LEMMA: "بجا", NORM: "بجا", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "بدان": [
            {ORTH: "ب", LEMMA: "ب", NORM: "ب", TAG: "ADP"},
            {ORTH: "دان", LEMMA: "دان", NORM: "دان", TAG: "NOUN"},
        ],
        "بدش": [
            {ORTH: "بد", LEMMA: "بد", NORM: "بد", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بدشان": [
            {ORTH: "بد", LEMMA: "بد", NORM: "بد", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "بدنم": [
            {ORTH: "بدن", LEMMA: "بدن", NORM: "بدن", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "بدهی‌ات": [
            {ORTH: "بدهی‌", LEMMA: "بدهی‌", NORM: "بدهی‌", TAG: "NOUN"},
            {ORTH: "ات", LEMMA: "ات", NORM: "ات", TAG: "NOUN"},
        ],
        "بدین": [
            {ORTH: "ب", LEMMA: "ب", NORM: "ب", TAG: "ADP"},
            {ORTH: "دین", LEMMA: "دین", NORM: "دین", TAG: "NOUN"},
        ],
        "برابرش": [
            {ORTH: "برابر", LEMMA: "برابر", NORM: "برابر", TAG: "ADP"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "برادرت": [
            {ORTH: "برادر", LEMMA: "برادر", NORM: "برادر", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "برادرش": [
            {ORTH: "برادر", LEMMA: "برادر", NORM: "برادر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "برایت": [
            {ORTH: "برای", LEMMA: "برای", NORM: "برای", TAG: "ADP"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "برایتان": [
            {ORTH: "برای", LEMMA: "برای", NORM: "برای", TAG: "ADP"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "برایش": [
            {ORTH: "برای", LEMMA: "برای", NORM: "برای", TAG: "ADP"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "برایشان": [
            {ORTH: "برای", LEMMA: "برای", NORM: "برای", TAG: "ADP"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "برایم": [
            {ORTH: "برای", LEMMA: "برای", NORM: "برای", TAG: "ADP"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "برایمان": [
            {ORTH: "برای", LEMMA: "برای", NORM: "برای", TAG: "ADP"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "برخوردارند": [
            {ORTH: "برخوردار", LEMMA: "برخوردار", NORM: "برخوردار", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "برنامه‌سازهاست": [
            {
                ORTH: "برنامه‌سازها",
                LEMMA: "برنامه‌سازها",
                NORM: "برنامه‌سازها",
                TAG: "NOUN",
            },
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "برهمش": [
            {ORTH: "برهم", LEMMA: "برهم", NORM: "برهم", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "برهنه‌اش": [
            {ORTH: "برهنه‌", LEMMA: "برهنه‌", NORM: "برهنه‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "برگهایش": [
            {ORTH: "برگها", LEMMA: "برگها", NORM: "برگها", TAG: "NOUN"},
            {ORTH: "یش", LEMMA: "یش", NORM: "یش", TAG: "NOUN"},
        ],
        "برین": [
            {ORTH: "بر", LEMMA: "بر", NORM: "بر", TAG: "ADP"},
            {ORTH: "ین", LEMMA: "ین", NORM: "ین", TAG: "NOUN"},
        ],
        "بزرگش": [
            {ORTH: "بزرگ", LEMMA: "بزرگ", NORM: "بزرگ", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بزرگ‌تری": [
            {ORTH: "بزرگ‌تر", LEMMA: "بزرگ‌تر", NORM: "بزرگ‌تر", TAG: "ADJ"},
            {ORTH: "ی", LEMMA: "ی", NORM: "ی", TAG: "VERB"},
        ],
        "بساطش": [
            {ORTH: "بساط", LEMMA: "بساط", NORM: "بساط", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بعدش": [
            {ORTH: "بعد", LEMMA: "بعد", NORM: "بعد", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بعضیهایشان": [
            {ORTH: "بعضیهای", LEMMA: "بعضیهای", NORM: "بعضیهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "بعضی‌شان": [
            {ORTH: "بعضی", LEMMA: "بعضی", NORM: "بعضی", TAG: "NOUN"},
            {ORTH: "‌شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "بقیه‌اش": [
            {ORTH: "بقیه‌", LEMMA: "بقیه‌", NORM: "بقیه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "بلندش": [
            {ORTH: "بلند", LEMMA: "بلند", NORM: "بلند", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بناگوشش": [
            {ORTH: "بناگوش", LEMMA: "بناگوش", NORM: "بناگوش", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بنظرم": [
            {ORTH: "ب", LEMMA: "ب", NORM: "ب", TAG: "ADP"},
            {ORTH: "نظر", LEMMA: "نظر", NORM: "نظر", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "بهت": [
            {ORTH: "به", LEMMA: "به", NORM: "به", TAG: "ADP"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "بهترش": [
            {ORTH: "بهتر", LEMMA: "بهتر", NORM: "بهتر", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بهترم": [
            {ORTH: "بهتر", LEMMA: "بهتر", NORM: "بهتر", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "بهتری": [
            {ORTH: "بهتر", LEMMA: "بهتر", NORM: "بهتر", TAG: "ADJ"},
            {ORTH: "ی", LEMMA: "ی", NORM: "ی", TAG: "VERB"},
        ],
        "بهش": [
            {ORTH: "به", LEMMA: "به", NORM: "به", TAG: "ADP"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "به‌شان": [
            {ORTH: "به‌", LEMMA: "به‌", NORM: "به‌", TAG: "ADP"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "بودمش": [
            {ORTH: "بودم", LEMMA: "بودم", NORM: "بودم", TAG: "VERB"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بودنش": [
            {ORTH: "بودن", LEMMA: "بودن", NORM: "بودن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بودن‌شان": [
            {ORTH: "بودن‌", LEMMA: "بودن‌", NORM: "بودن‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "بوستانش": [
            {ORTH: "بوستان", LEMMA: "بوستان", NORM: "بوستان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بویش": [
            {ORTH: "بو", LEMMA: "بو", NORM: "بو", TAG: "NOUN"},
            {ORTH: "یش", LEMMA: "یش", NORM: "یش", TAG: "NOUN"},
        ],
        "بچه‌اش": [
            {ORTH: "بچه‌", LEMMA: "بچه‌", NORM: "بچه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "بچه‌م": [
            {ORTH: "بچه‌", LEMMA: "بچه‌", NORM: "بچه‌", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "بچه‌هایش": [
            {ORTH: "بچه‌های", LEMMA: "بچه‌های", NORM: "بچه‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بیانیه‌شان": [
            {ORTH: "بیانیه‌", LEMMA: "بیانیه‌", NORM: "بیانیه‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "بیدارم": [
            {ORTH: "بیدار", LEMMA: "بیدار", NORM: "بیدار", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "بیناتری": [
            {ORTH: "بیناتر", LEMMA: "بیناتر", NORM: "بیناتر", TAG: "ADJ"},
            {ORTH: "ی", LEMMA: "ی", NORM: "ی", TAG: "VERB"},
        ],
        "بی‌اطلاعند": [
            {ORTH: "بی‌اطلاع", LEMMA: "بی‌اطلاع", NORM: "بی‌اطلاع", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "بی‌اطلاعید": [
            {ORTH: "بی‌اطلاع", LEMMA: "بی‌اطلاع", NORM: "بی‌اطلاع", TAG: "ADJ"},
            {ORTH: "ید", LEMMA: "ید", NORM: "ید", TAG: "VERB"},
        ],
        "بی‌بهره‌اند": [
            {ORTH: "بی‌بهره‌", LEMMA: "بی‌بهره‌", NORM: "بی‌بهره‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "بی‌تفاوتند": [
            {ORTH: "بی‌تفاوت", LEMMA: "بی‌تفاوت", NORM: "بی‌تفاوت", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "بی‌حسابش": [
            {ORTH: "بی‌حساب", LEMMA: "بی‌حساب", NORM: "بی‌حساب", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "بی‌نیش": [
            {ORTH: "بی‌نی", LEMMA: "بی‌نی", NORM: "بی‌نی", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "تجربه‌هایم": [
            {ORTH: "تجربه‌ها", LEMMA: "تجربه‌ها", NORM: "تجربه‌ها", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "NOUN"},
        ],
        "تحریم‌هاست": [
            {ORTH: "تحریم‌ها", LEMMA: "تحریم‌ها", NORM: "تحریم‌ها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "تحولند": [
            {ORTH: "تحول", LEMMA: "تحول", NORM: "تحول", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "تخیلی‌اش": [
            {ORTH: "تخیلی‌", LEMMA: "تخیلی‌", NORM: "تخیلی‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "ترا": [
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
            {ORTH: "را", LEMMA: "را", NORM: "را", TAG: "PART"},
        ],
        "ترسشان": [
            {ORTH: "ترس", LEMMA: "ترس", NORM: "ترس", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "ترکش": [
            {ORTH: "ترک", LEMMA: "ترک", NORM: "ترک", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "تشنه‌ت": [
            {ORTH: "تشنه‌", LEMMA: "تشنه‌", NORM: "تشنه‌", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "تشکیلاتی‌اش": [
            {ORTH: "تشکیلاتی‌", LEMMA: "تشکیلاتی‌", NORM: "تشکیلاتی‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "تعلقش": [
            {ORTH: "تعلق", LEMMA: "تعلق", NORM: "تعلق", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "تلاششان": [
            {ORTH: "تلاش", LEMMA: "تلاش", NORM: "تلاش", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "تلاشمان": [
            {ORTH: "تلاش", LEMMA: "تلاش", NORM: "تلاش", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "تماشاگرش": [
            {ORTH: "تماشاگر", LEMMA: "تماشاگر", NORM: "تماشاگر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "تمامشان": [
            {ORTH: "تمام", LEMMA: "تمام", NORM: "تمام", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "تنش": [
            {ORTH: "تن", LEMMA: "تن", NORM: "تن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "تنمان": [
            {ORTH: "تن", LEMMA: "تن", NORM: "تن", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "تنهایی‌اش": [
            {ORTH: "تنهایی‌", LEMMA: "تنهایی‌", NORM: "تنهایی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "توانایی‌اش": [
            {ORTH: "توانایی‌", LEMMA: "توانایی‌", NORM: "توانایی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "توجهش": [
            {ORTH: "توجه", LEMMA: "توجه", NORM: "توجه", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "توست": [
            {ORTH: "تو", LEMMA: "تو", NORM: "تو", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "توصیه‌اش": [
            {ORTH: "توصیه‌", LEMMA: "توصیه‌", NORM: "توصیه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "تیغه‌اش": [
            {ORTH: "تیغه‌", LEMMA: "تیغه‌", NORM: "تیغه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "جاست": [
            {ORTH: "جا", LEMMA: "جا", NORM: "جا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "جامعه‌اند": [
            {ORTH: "جامعه‌", LEMMA: "جامعه‌", NORM: "جامعه‌", TAG: "NOUN"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "جانم": [
            {ORTH: "جان", LEMMA: "جان", NORM: "جان", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "جایش": [
            {ORTH: "جای", LEMMA: "جای", NORM: "جای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "جایشان": [
            {ORTH: "جای", LEMMA: "جای", NORM: "جای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "جدیدش": [
            {ORTH: "جدید", LEMMA: "جدید", NORM: "جدید", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "جرمزاست": [
            {ORTH: "جرمزا", LEMMA: "جرمزا", NORM: "جرمزا", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "جلوست": [
            {ORTH: "جلو", LEMMA: "جلو", NORM: "جلو", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "جلویش": [
            {ORTH: "جلوی", LEMMA: "جلوی", NORM: "جلوی", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "جمهوریست": [
            {ORTH: "جمهوری", LEMMA: "جمهوری", NORM: "جمهوری", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "جنسش": [
            {ORTH: "جنس", LEMMA: "جنس", NORM: "جنس", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "جنس‌اند": [
            {ORTH: "جنس‌", LEMMA: "جنس‌", NORM: "جنس‌", TAG: "NOUN"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "جوانانش": [
            {ORTH: "جوانان", LEMMA: "جوانان", NORM: "جوانان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "جویش": [
            {ORTH: "جوی", LEMMA: "جوی", NORM: "جوی", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "جگرش": [
            {ORTH: "جگر", LEMMA: "جگر", NORM: "جگر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "حاضرم": [
            {ORTH: "حاضر", LEMMA: "حاضر", NORM: "حاضر", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "حالتهایشان": [
            {ORTH: "حالتهای", LEMMA: "حالتهای", NORM: "حالتهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "حالیست": [
            {ORTH: "حالی", LEMMA: "حالی", NORM: "حالی", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "حالی‌مان": [
            {ORTH: "حالی‌", LEMMA: "حالی‌", NORM: "حالی‌", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "حاکیست": [
            {ORTH: "حاکی", LEMMA: "حاکی", NORM: "حاکی", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "حرامزادگی‌اش": [
            {ORTH: "حرامزادگی‌", LEMMA: "حرامزادگی‌", NORM: "حرامزادگی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "حرفتان": [
            {ORTH: "حرف", LEMMA: "حرف", NORM: "حرف", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "حرفش": [
            {ORTH: "حرف", LEMMA: "حرف", NORM: "حرف", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "حرفشان": [
            {ORTH: "حرف", LEMMA: "حرف", NORM: "حرف", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "حرفم": [
            {ORTH: "حرف", LEMMA: "حرف", NORM: "حرف", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "حرف‌های‌شان": [
            {ORTH: "حرف‌های‌", LEMMA: "حرف‌های‌", NORM: "حرف‌های‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "حرکتمان": [
            {ORTH: "حرکت", LEMMA: "حرکت", NORM: "حرکت", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "حریفانشان": [
            {ORTH: "حریفان", LEMMA: "حریفان", NORM: "حریفان", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "حضورشان": [
            {ORTH: "حضور", LEMMA: "حضور", NORM: "حضور", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "حمایتش": [
            {ORTH: "حمایت", LEMMA: "حمایت", NORM: "حمایت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "حواسش": [
            {ORTH: "حواس", LEMMA: "حواس", NORM: "حواس", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "حواسشان": [
            {ORTH: "حواس", LEMMA: "حواس", NORM: "حواس", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "حوصله‌مان": [
            {ORTH: "حوصله‌", LEMMA: "حوصله‌", NORM: "حوصله‌", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "حکومتش": [
            {ORTH: "حکومت", LEMMA: "حکومت", NORM: "حکومت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "حکومتشان": [
            {ORTH: "حکومت", LEMMA: "حکومت", NORM: "حکومت", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "حیفم": [
            {ORTH: "حیف", LEMMA: "حیف", NORM: "حیف", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "خاندانش": [
            {ORTH: "خاندان", LEMMA: "خاندان", NORM: "خاندان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خانه‌اش": [
            {ORTH: "خانه‌", LEMMA: "خانه‌", NORM: "خانه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "خانه‌شان": [
            {ORTH: "خانه‌", LEMMA: "خانه‌", NORM: "خانه‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "خانه‌مان": [
            {ORTH: "خانه‌", LEMMA: "خانه‌", NORM: "خانه‌", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "خانه‌هایشان": [
            {ORTH: "خانه‌های", LEMMA: "خانه‌های", NORM: "خانه‌های", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "خانواده‌ات": [
            {ORTH: "خانواده", LEMMA: "خانواده", NORM: "خانواده", TAG: "NOUN"},
            {ORTH: "‌ات", LEMMA: "ات", NORM: "ات", TAG: "NOUN"},
        ],
        "خانواده‌اش": [
            {ORTH: "خانواده‌", LEMMA: "خانواده‌", NORM: "خانواده‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "خانواده‌ام": [
            {ORTH: "خانواده‌", LEMMA: "خانواده‌", NORM: "خانواده‌", TAG: "NOUN"},
            {ORTH: "ام", LEMMA: "ام", NORM: "ام", TAG: "NOUN"},
        ],
        "خانواده‌شان": [
            {ORTH: "خانواده‌", LEMMA: "خانواده‌", NORM: "خانواده‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "خداست": [
            {ORTH: "خدا", LEMMA: "خدا", NORM: "خدا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "خدایش": [
            {ORTH: "خدا", LEMMA: "خدا", NORM: "خدا", TAG: "NOUN"},
            {ORTH: "یش", LEMMA: "یش", NORM: "یش", TAG: "NOUN"},
        ],
        "خدایشان": [
            {ORTH: "خدای", LEMMA: "خدای", NORM: "خدای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "خردسالش": [
            {ORTH: "خردسال", LEMMA: "خردسال", NORM: "خردسال", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خروپفشان": [
            {ORTH: "خروپف", LEMMA: "خروپف", NORM: "خروپف", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "خسته‌ای": [
            {ORTH: "خسته‌", LEMMA: "خسته‌", NORM: "خسته‌", TAG: "ADJ"},
            {ORTH: "ای", LEMMA: "ای", NORM: "ای", TAG: "VERB"},
        ],
        "خطت": [
            {ORTH: "خط", LEMMA: "خط", NORM: "خط", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "خوابمان": [
            {ORTH: "خواب", LEMMA: "خواب", NORM: "خواب", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "خواندنش": [
            {ORTH: "خواندن", LEMMA: "خواندن", NORM: "خواندن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خواهرش": [
            {ORTH: "خواهر", LEMMA: "خواهر", NORM: "خواهر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خوبش": [
            {ORTH: "خوب", LEMMA: "خوب", NORM: "خوب", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خودت": [
            {ORTH: "خود", LEMMA: "خود", NORM: "خود", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "خودتان": [
            {ORTH: "خود", LEMMA: "خود", NORM: "خود", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "خودش": [
            {ORTH: "خود", LEMMA: "خود", NORM: "خود", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خودشان": [
            {ORTH: "خود", LEMMA: "خود", NORM: "خود", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "خودمان": [
            {ORTH: "خود", LEMMA: "خود", NORM: "خود", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "خوردمان": [
            {ORTH: "خورد", LEMMA: "خورد", NORM: "خورد", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "خوردنشان": [
            {ORTH: "خوردن", LEMMA: "خوردن", NORM: "خوردن", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "خوشش": [
            {ORTH: "خوش", LEMMA: "خوش", NORM: "خوش", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خوشوقتم": [
            {ORTH: "خوشوقت", LEMMA: "خوشوقت", NORM: "خوشوقت", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "خونشان": [
            {ORTH: "خون", LEMMA: "خون", NORM: "خون", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "خویش": [
            {ORTH: "خوی", LEMMA: "خوی", NORM: "خوی", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خویشتنم": [
            {ORTH: "خویشتن", LEMMA: "خویشتن", NORM: "خویشتن", TAG: "VERB"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "خیالش": [
            {ORTH: "خیال", LEMMA: "خیال", NORM: "خیال", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "خیسش": [
            {ORTH: "خیس", LEMMA: "خیس", NORM: "خیس", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "داراست": [
            {ORTH: "دارا", LEMMA: "دارا", NORM: "دارا", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "داستانهایش": [
            {ORTH: "داستانهای", LEMMA: "داستانهای", NORM: "داستانهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دخترمان": [
            {ORTH: "دختر", LEMMA: "دختر", NORM: "دختر", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "دخیلند": [
            {ORTH: "دخیل", LEMMA: "دخیل", NORM: "دخیل", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "درباره‌ات": [
            {ORTH: "درباره", LEMMA: "درباره", NORM: "درباره", TAG: "ADP"},
            {ORTH: "‌ات", LEMMA: "ات", NORM: "ات", TAG: "NOUN"},
        ],
        "درباره‌اش": [
            {ORTH: "درباره‌", LEMMA: "درباره‌", NORM: "درباره‌", TAG: "ADP"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "دردش": [
            {ORTH: "درد", LEMMA: "درد", NORM: "درد", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دردشان": [
            {ORTH: "درد", LEMMA: "درد", NORM: "درد", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "درسته": [
            {ORTH: "درست", LEMMA: "درست", NORM: "درست", TAG: "ADJ"},
            {ORTH: "ه", LEMMA: "ه", NORM: "ه", TAG: "VERB"},
        ],
        "درش": [
            {ORTH: "در", LEMMA: "در", NORM: "در", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "درون‌شان": [
            {ORTH: "درون‌", LEMMA: "درون‌", NORM: "درون‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "درین": [
            {ORTH: "در", LEMMA: "در", NORM: "در", TAG: "ADP"},
            {ORTH: "ین", LEMMA: "ین", NORM: "ین", TAG: "NOUN"},
        ],
        "دریچه‌هایش": [
            {ORTH: "دریچه‌های", LEMMA: "دریچه‌های", NORM: "دریچه‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دزدانش": [
            {ORTH: "دزدان", LEMMA: "دزدان", NORM: "دزدان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دستت": [
            {ORTH: "دست", LEMMA: "دست", NORM: "دست", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "دستش": [
            {ORTH: "دست", LEMMA: "دست", NORM: "دست", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دستمان": [
            {ORTH: "دست", LEMMA: "دست", NORM: "دست", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "دستهایشان": [
            {ORTH: "دستهای", LEMMA: "دستهای", NORM: "دستهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "دست‌یافتنی‌ست": [
            {
                ORTH: "دست‌یافتنی‌",
                LEMMA: "دست‌یافتنی‌",
                NORM: "دست‌یافتنی‌",
                TAG: "ADJ",
            },
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "دشمنند": [
            {ORTH: "دشمن", LEMMA: "دشمن", NORM: "دشمن", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "دشمنیشان": [
            {ORTH: "دشمنی", LEMMA: "دشمنی", NORM: "دشمنی", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "دشمنیم": [
            {ORTH: "دشمن", LEMMA: "دشمن", NORM: "دشمن", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "دفترش": [
            {ORTH: "دفتر", LEMMA: "دفتر", NORM: "دفتر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دفنشان": [
            {ORTH: "دفن", LEMMA: "دفن", NORM: "دفن", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "دلت": [
            {ORTH: "دل", LEMMA: "دل", NORM: "دل", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "دلش": [
            {ORTH: "دل", LEMMA: "دل", NORM: "دل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دلشان": [
            {ORTH: "دل", LEMMA: "دل", NORM: "دل", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "دلم": [
            {ORTH: "دل", LEMMA: "دل", NORM: "دل", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "دلیلش": [
            {ORTH: "دلیل", LEMMA: "دلیل", NORM: "دلیل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دنبالش": [
            {ORTH: "دنبال", LEMMA: "دنبال", NORM: "دنبال", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دنباله‌اش": [
            {ORTH: "دنباله‌", LEMMA: "دنباله‌", NORM: "دنباله‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "دهاتی‌هایش": [
            {ORTH: "دهاتی‌های", LEMMA: "دهاتی‌های", NORM: "دهاتی‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دهانت": [
            {ORTH: "دهان", LEMMA: "دهان", NORM: "دهان", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "دهنش": [
            {ORTH: "دهن", LEMMA: "دهن", NORM: "دهن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دورش": [
            {ORTH: "دور", LEMMA: "دور", NORM: "دور", TAG: "ADV"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دوروبریهاشان": [
            {ORTH: "دوروبریها", LEMMA: "دوروبریها", NORM: "دوروبریها", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "دوستانش": [
            {ORTH: "دوستان", LEMMA: "دوستان", NORM: "دوستان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دوستانشان": [
            {ORTH: "دوستان", LEMMA: "دوستان", NORM: "دوستان", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "دوستت": [
            {ORTH: "دوست", LEMMA: "دوست", NORM: "دوست", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "دوستش": [
            {ORTH: "دوست", LEMMA: "دوست", NORM: "دوست", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دومش": [
            {ORTH: "دوم", LEMMA: "دوم", NORM: "دوم", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دویدنش": [
            {ORTH: "دویدن", LEMMA: "دویدن", NORM: "دویدن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دکورهایمان": [
            {ORTH: "دکورهای", LEMMA: "دکورهای", NORM: "دکورهای", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "دیدگاهش": [
            {ORTH: "دیدگاه", LEMMA: "دیدگاه", NORM: "دیدگاه", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دیرت": [
            {ORTH: "دیر", LEMMA: "دیر", NORM: "دیر", TAG: "ADV"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "دیرم": [
            {ORTH: "دیر", LEMMA: "دیر", NORM: "دیر", TAG: "ADV"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "دینت": [
            {ORTH: "دین", LEMMA: "دین", NORM: "دین", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "دینش": [
            {ORTH: "دین", LEMMA: "دین", NORM: "دین", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دین‌شان": [
            {ORTH: "دین‌", LEMMA: "دین‌", NORM: "دین‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "دیواره‌هایش": [
            {ORTH: "دیواره‌های", LEMMA: "دیواره‌های", NORM: "دیواره‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "دیوانه‌ای": [
            {ORTH: "دیوانه‌", LEMMA: "دیوانه‌", NORM: "دیوانه‌", TAG: "ADJ"},
            {ORTH: "ای", LEMMA: "ای", NORM: "ای", TAG: "VERB"},
        ],
        "دیوی": [
            {ORTH: "دیو", LEMMA: "دیو", NORM: "دیو", TAG: "NOUN"},
            {ORTH: "ی", LEMMA: "ی", NORM: "ی", TAG: "VERB"},
        ],
        "دیگرم": [
            {ORTH: "دیگر", LEMMA: "دیگر", NORM: "دیگر", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "دیگرمان": [
            {ORTH: "دیگر", LEMMA: "دیگر", NORM: "دیگر", TAG: "ADJ"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "ذهنش": [
            {ORTH: "ذهن", LEMMA: "ذهن", NORM: "ذهن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "ذهنشان": [
            {ORTH: "ذهن", LEMMA: "ذهن", NORM: "ذهن", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "ذهنم": [
            {ORTH: "ذهن", LEMMA: "ذهن", NORM: "ذهن", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "رئوسش": [
            {ORTH: "رئوس", LEMMA: "رئوس", NORM: "رئوس", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "راهشان": [
            {ORTH: "راه", LEMMA: "راه", NORM: "راه", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "راهگشاست": [
            {ORTH: "راهگشا", LEMMA: "راهگشا", NORM: "راهگشا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "رایانه‌هایشان": [
            {ORTH: "رایانه‌های", LEMMA: "رایانه‌های", NORM: "رایانه‌های", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "رعایتشان": [
            {ORTH: "رعایت", LEMMA: "رعایت", NORM: "رعایت", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "رفتارش": [
            {ORTH: "رفتار", LEMMA: "رفتار", NORM: "رفتار", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "رفتارشان": [
            {ORTH: "رفتار", LEMMA: "رفتار", NORM: "رفتار", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "رفتارمان": [
            {ORTH: "رفتار", LEMMA: "رفتار", NORM: "رفتار", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "رفتارهاست": [
            {ORTH: "رفتارها", LEMMA: "رفتارها", NORM: "رفتارها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "رفتارهایشان": [
            {ORTH: "رفتارهای", LEMMA: "رفتارهای", NORM: "رفتارهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "رفقایم": [
            {ORTH: "رفقا", LEMMA: "رفقا", NORM: "رفقا", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "NOUN"},
        ],
        "رقیق‌ترش": [
            {ORTH: "رقیق‌تر", LEMMA: "رقیق‌تر", NORM: "رقیق‌تر", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "رنجند": [
            {ORTH: "رنج", LEMMA: "رنج", NORM: "رنج", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "رهگشاست": [
            {ORTH: "رهگشا", LEMMA: "رهگشا", NORM: "رهگشا", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "رواست": [
            {ORTH: "روا", LEMMA: "روا", NORM: "روا", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "روبروست": [
            {ORTH: "روبرو", LEMMA: "روبرو", NORM: "روبرو", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "روحی‌اش": [
            {ORTH: "روحی‌", LEMMA: "روحی‌", NORM: "روحی‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "روزنامه‌اش": [
            {ORTH: "روزنامه‌", LEMMA: "روزنامه‌", NORM: "روزنامه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "روزه‌ست": [
            {ORTH: "روزه‌", LEMMA: "روزه‌", NORM: "روزه‌", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "روسری‌اش": [
            {ORTH: "روسری‌", LEMMA: "روسری‌", NORM: "روسری‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "روشتان": [
            {ORTH: "روش", LEMMA: "روش", NORM: "روش", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "رویش": [
            {ORTH: "روی", LEMMA: "روی", NORM: "روی", TAG: "ADP"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "زبانش": [
            {ORTH: "زبان", LEMMA: "زبان", NORM: "زبان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "زحماتشان": [
            {ORTH: "زحمات", LEMMA: "زحمات", NORM: "زحمات", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "زدنهایشان": [
            {ORTH: "زدنهای", LEMMA: "زدنهای", NORM: "زدنهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "زرنگشان": [
            {ORTH: "زرنگ", LEMMA: "زرنگ", NORM: "زرنگ", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "زشتش": [
            {ORTH: "زشت", LEMMA: "زشت", NORM: "زشت", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "زشتکارانند": [
            {ORTH: "زشتکاران", LEMMA: "زشتکاران", NORM: "زشتکاران", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "زلفش": [
            {ORTH: "زلف", LEMMA: "زلف", NORM: "زلف", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "زمن": [
            {ORTH: "ز", LEMMA: "ز", NORM: "ز", TAG: "ADP"},
            {ORTH: "من", LEMMA: "من", NORM: "من", TAG: "NOUN"},
        ],
        "زنبوری‌اش": [
            {ORTH: "زنبوری‌", LEMMA: "زنبوری‌", NORM: "زنبوری‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "زندانم": [
            {ORTH: "زندان", LEMMA: "زندان", NORM: "زندان", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "زنده‌ام": [
            {ORTH: "زنده‌", LEMMA: "زنده‌", NORM: "زنده‌", TAG: "ADJ"},
            {ORTH: "ام", LEMMA: "ام", NORM: "ام", TAG: "VERB"},
        ],
        "زندگانی‌اش": [
            {ORTH: "زندگانی‌", LEMMA: "زندگانی‌", NORM: "زندگانی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "زندگی‌اش": [
            {ORTH: "زندگی‌", LEMMA: "زندگی‌", NORM: "زندگی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "زندگی‌ام": [
            {ORTH: "زندگی‌", LEMMA: "زندگی‌", NORM: "زندگی‌", TAG: "NOUN"},
            {ORTH: "ام", LEMMA: "ام", NORM: "ام", TAG: "NOUN"},
        ],
        "زندگی‌شان": [
            {ORTH: "زندگی‌", LEMMA: "زندگی‌", NORM: "زندگی‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "زنش": [
            {ORTH: "زن", LEMMA: "زن", NORM: "زن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "زنند": [
            {ORTH: "زن", LEMMA: "زن", NORM: "زن", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "زو": [
            {ORTH: "ز", LEMMA: "ز", NORM: "ز", TAG: "ADP"},
            {ORTH: "و", LEMMA: "و", NORM: "و", TAG: "NOUN"},
        ],
        "زیاده": [
            {ORTH: "زیاد", LEMMA: "زیاد", NORM: "زیاد", TAG: "ADJ"},
            {ORTH: "ه", LEMMA: "ه", NORM: "ه", TAG: "VERB"},
        ],
        "زیباست": [
            {ORTH: "زیبا", LEMMA: "زیبا", NORM: "زیبا", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "زیبایش": [
            {ORTH: "زیبای", LEMMA: "زیبای", NORM: "زیبای", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "زیبایی": [
            {ORTH: "زیبای", LEMMA: "زیبای", NORM: "زیبای", TAG: "ADJ"},
            {ORTH: "ی", LEMMA: "ی", NORM: "ی", TAG: "VERB"},
        ],
        "زیربناست": [
            {ORTH: "زیربنا", LEMMA: "زیربنا", NORM: "زیربنا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "زیرک‌اند": [
            {ORTH: "زیرک‌", LEMMA: "زیرک‌", NORM: "زیرک‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "سؤالتان": [
            {ORTH: "سؤال", LEMMA: "سؤال", NORM: "سؤال", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "سؤالم": [
            {ORTH: "سؤال", LEMMA: "سؤال", NORM: "سؤال", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "سابقه‌اش": [
            {ORTH: "سابقه‌", LEMMA: "سابقه‌", NORM: "سابقه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "ساختنم": [
            {ORTH: "ساختن", LEMMA: "ساختن", NORM: "ساختن", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "ساده‌اش": [
            {ORTH: "ساده‌", LEMMA: "ساده‌", NORM: "ساده‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "ساده‌اند": [
            {ORTH: "ساده‌", LEMMA: "ساده‌", NORM: "ساده‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "سازمانش": [
            {ORTH: "سازمان", LEMMA: "سازمان", NORM: "سازمان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "ساعتم": [
            {ORTH: "ساعت", LEMMA: "ساعت", NORM: "ساعت", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "سالته": [
            {ORTH: "سال", LEMMA: "سال", NORM: "سال", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
            {ORTH: "ه", LEMMA: "ه", NORM: "ه", TAG: "VERB"},
        ],
        "سالش": [
            {ORTH: "سال", LEMMA: "سال", NORM: "سال", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سالهاست": [
            {ORTH: "سالها", LEMMA: "سالها", NORM: "سالها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "ساله‌اش": [
            {ORTH: "ساله‌", LEMMA: "ساله‌", NORM: "ساله‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "ساکتند": [
            {ORTH: "ساکت", LEMMA: "ساکت", NORM: "ساکت", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "ساکنند": [
            {ORTH: "ساکن", LEMMA: "ساکن", NORM: "ساکن", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "سبزشان": [
            {ORTH: "سبز", LEMMA: "سبز", NORM: "سبز", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "سبیل‌مان": [
            {ORTH: "سبیل‌", LEMMA: "سبیل‌", NORM: "سبیل‌", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "ستم‌هایش": [
            {ORTH: "ستم‌های", LEMMA: "ستم‌های", NORM: "ستم‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سخنانش": [
            {ORTH: "سخنان", LEMMA: "سخنان", NORM: "سخنان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سخنانشان": [
            {ORTH: "سخنان", LEMMA: "سخنان", NORM: "سخنان", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "سخنتان": [
            {ORTH: "سخن", LEMMA: "سخن", NORM: "سخن", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "سخنش": [
            {ORTH: "سخن", LEMMA: "سخن", NORM: "سخن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سخنم": [
            {ORTH: "سخن", LEMMA: "سخن", NORM: "سخن", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "سردش": [
            {ORTH: "سرد", LEMMA: "سرد", NORM: "سرد", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سرزمینشان": [
            {ORTH: "سرزمین", LEMMA: "سرزمین", NORM: "سرزمین", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "سرش": [
            {ORTH: "سر", LEMMA: "سر", NORM: "سر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سرمایه‌دارهاست": [
            {
                ORTH: "سرمایه‌دارها",
                LEMMA: "سرمایه‌دارها",
                NORM: "سرمایه‌دارها",
                TAG: "NOUN",
            },
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "سرنوشتش": [
            {ORTH: "سرنوشت", LEMMA: "سرنوشت", NORM: "سرنوشت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سرنوشتشان": [
            {ORTH: "سرنوشت", LEMMA: "سرنوشت", NORM: "سرنوشت", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "سروتهش": [
            {ORTH: "سروته", LEMMA: "سروته", NORM: "سروته", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سرچشمه‌اش": [
            {ORTH: "سرچشمه‌", LEMMA: "سرچشمه‌", NORM: "سرچشمه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "سقمش": [
            {ORTH: "سقم", LEMMA: "سقم", NORM: "سقم", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سنش": [
            {ORTH: "سن", LEMMA: "سن", NORM: "سن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سپاهش": [
            {ORTH: "سپاه", LEMMA: "سپاه", NORM: "سپاه", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "سیاسیشان": [
            {ORTH: "سیاسی", LEMMA: "سیاسی", NORM: "سیاسی", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "سیاه‌چاله‌هاست": [
            {
                ORTH: "سیاه‌چاله‌ها",
                LEMMA: "سیاه‌چاله‌ها",
                NORM: "سیاه‌چاله‌ها",
                TAG: "NOUN",
            },
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "شاخه‌هایشان": [
            {ORTH: "شاخه‌های", LEMMA: "شاخه‌های", NORM: "شاخه‌های", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "شالوده‌اش": [
            {ORTH: "شالوده‌", LEMMA: "شالوده‌", NORM: "شالوده‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "شانه‌هایش": [
            {ORTH: "شانه‌های", LEMMA: "شانه‌های", NORM: "شانه‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "شاهدیم": [
            {ORTH: "شاهد", LEMMA: "شاهد", NORM: "شاهد", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "شاهکارهایش": [
            {ORTH: "شاهکارهای", LEMMA: "شاهکارهای", NORM: "شاهکارهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "شخصیتش": [
            {ORTH: "شخصیت", LEMMA: "شخصیت", NORM: "شخصیت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "شدنشان": [
            {ORTH: "شدن", LEMMA: "شدن", NORM: "شدن", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "شرکتیست": [
            {ORTH: "شرکتی", LEMMA: "شرکتی", NORM: "شرکتی", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "شعارهاشان": [
            {ORTH: "شعارها", LEMMA: "شعارها", NORM: "شعارها", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "شعورش": [
            {ORTH: "شعور", LEMMA: "شعور", NORM: "شعور", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "شغلش": [
            {ORTH: "شغل", LEMMA: "شغل", NORM: "شغل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "شماست": [
            {ORTH: "شما", LEMMA: "شما", NORM: "شما", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "شمشیرش": [
            {ORTH: "شمشیر", LEMMA: "شمشیر", NORM: "شمشیر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "شنیدنش": [
            {ORTH: "شنیدن", LEMMA: "شنیدن", NORM: "شنیدن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "شوراست": [
            {ORTH: "شورا", LEMMA: "شورا", NORM: "شورا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "شومت": [
            {ORTH: "شوم", LEMMA: "شوم", NORM: "شوم", TAG: "ADJ"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "شیرینترش": [
            {ORTH: "شیرینتر", LEMMA: "شیرینتر", NORM: "شیرینتر", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "شیطان‌اند": [
            {ORTH: "شیطان‌", LEMMA: "شیطان‌", NORM: "شیطان‌", TAG: "NOUN"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "شیوه‌هاست": [
            {ORTH: "شیوه‌ها", LEMMA: "شیوه‌ها", NORM: "شیوه‌ها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "صاحبش": [
            {ORTH: "صاحب", LEMMA: "صاحب", NORM: "صاحب", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "صحنه‌اش": [
            {ORTH: "صحنه‌", LEMMA: "صحنه‌", NORM: "صحنه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "صدایش": [
            {ORTH: "صدای", LEMMA: "صدای", NORM: "صدای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "صددند": [
            {ORTH: "صدد", LEMMA: "صدد", NORM: "صدد", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "صندوق‌هاست": [
            {ORTH: "صندوق‌ها", LEMMA: "صندوق‌ها", NORM: "صندوق‌ها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "صندوق‌هایش": [
            {ORTH: "صندوق‌های", LEMMA: "صندوق‌های", NORM: "صندوق‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "صورتش": [
            {ORTH: "صورت", LEMMA: "صورت", NORM: "صورت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "ضروری‌اند": [
            {ORTH: "ضروری‌", LEMMA: "ضروری‌", NORM: "ضروری‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "ضمیرش": [
            {ORTH: "ضمیر", LEMMA: "ضمیر", NORM: "ضمیر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "طرفش": [
            {ORTH: "طرف", LEMMA: "طرف", NORM: "طرف", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "طلسمش": [
            {ORTH: "طلسم", LEMMA: "طلسم", NORM: "طلسم", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "طوره": [
            {ORTH: "طور", LEMMA: "طور", NORM: "طور", TAG: "NOUN"},
            {ORTH: "ه", LEMMA: "ه", NORM: "ه", TAG: "VERB"},
        ],
        "عاشوراست": [
            {ORTH: "عاشورا", LEMMA: "عاشورا", NORM: "عاشورا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "عبارتند": [
            {ORTH: "عبارت", LEMMA: "عبارت", NORM: "عبارت", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "عزیزانتان": [
            {ORTH: "عزیزان", LEMMA: "عزیزان", NORM: "عزیزان", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "عزیزانش": [
            {ORTH: "عزیزان", LEMMA: "عزیزان", NORM: "عزیزان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "عزیزش": [
            {ORTH: "عزیز", LEMMA: "عزیز", NORM: "عزیز", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "عشرت‌طلبی‌اش": [
            {ORTH: "عشرت‌طلبی‌", LEMMA: "عشرت‌طلبی‌", NORM: "عشرت‌طلبی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "عقبیم": [
            {ORTH: "عقب", LEMMA: "عقب", NORM: "عقب", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "علاقه‌اش": [
            {ORTH: "علاقه‌", LEMMA: "علاقه‌", NORM: "علاقه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "علمیمان": [
            {ORTH: "علمی", LEMMA: "علمی", NORM: "علمی", TAG: "ADJ"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "عمرش": [
            {ORTH: "عمر", LEMMA: "عمر", NORM: "عمر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "عمرشان": [
            {ORTH: "عمر", LEMMA: "عمر", NORM: "عمر", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "عملش": [
            {ORTH: "عمل", LEMMA: "عمل", NORM: "عمل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "عملی‌اند": [
            {ORTH: "عملی‌", LEMMA: "عملی‌", NORM: "عملی‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "عمویت": [
            {ORTH: "عموی", LEMMA: "عموی", NORM: "عموی", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "عمویش": [
            {ORTH: "عموی", LEMMA: "عموی", NORM: "عموی", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "عمیقش": [
            {ORTH: "عمیق", LEMMA: "عمیق", NORM: "عمیق", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "عواملش": [
            {ORTH: "عوامل", LEMMA: "عوامل", NORM: "عوامل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "عوضشان": [
            {ORTH: "عوض", LEMMA: "عوض", NORM: "عوض", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "غذایی‌شان": [
            {ORTH: "غذایی‌", LEMMA: "غذایی‌", NORM: "غذایی‌", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "غریبه‌اند": [
            {ORTH: "غریبه‌", LEMMA: "غریبه‌", NORM: "غریبه‌", TAG: "NOUN"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "غلامانش": [
            {ORTH: "غلامان", LEMMA: "غلامان", NORM: "غلامان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "غلطهاست": [
            {ORTH: "غلطها", LEMMA: "غلطها", NORM: "غلطها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "فراموشتان": [
            {ORTH: "فراموش", LEMMA: "فراموش", NORM: "فراموش", TAG: "ADJ"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "فردی‌اند": [
            {ORTH: "فردی‌", LEMMA: "فردی‌", NORM: "فردی‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "فرزندانش": [
            {ORTH: "فرزندان", LEMMA: "فرزندان", NORM: "فرزندان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "فرزندش": [
            {ORTH: "فرزند", LEMMA: "فرزند", NORM: "فرزند", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "فرم‌هایش": [
            {ORTH: "فرم‌های", LEMMA: "فرم‌های", NORM: "فرم‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "فرهنگی‌مان": [
            {ORTH: "فرهنگی‌", LEMMA: "فرهنگی‌", NORM: "فرهنگی‌", TAG: "ADJ"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "فریادشان": [
            {ORTH: "فریاد", LEMMA: "فریاد", NORM: "فریاد", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "فضایی‌شان": [
            {ORTH: "فضایی‌", LEMMA: "فضایی‌", NORM: "فضایی‌", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "فقیرشان": [
            {ORTH: "فقیر", LEMMA: "فقیر", NORM: "فقیر", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "فوری‌شان": [
            {ORTH: "فوری‌", LEMMA: "فوری‌", NORM: "فوری‌", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "قائلند": [
            {ORTH: "قائل", LEMMA: "قائل", NORM: "قائل", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "قائلیم": [
            {ORTH: "قائل", LEMMA: "قائل", NORM: "قائل", TAG: "ADJ"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "قادرند": [
            {ORTH: "قادر", LEMMA: "قادر", NORM: "قادر", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "قانونمندش": [
            {ORTH: "قانونمند", LEMMA: "قانونمند", NORM: "قانونمند", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "قبلند": [
            {ORTH: "قبل", LEMMA: "قبل", NORM: "قبل", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "قبلی‌اش": [
            {ORTH: "قبلی‌", LEMMA: "قبلی‌", NORM: "قبلی‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "قبلی‌مان": [
            {ORTH: "قبلی‌", LEMMA: "قبلی‌", NORM: "قبلی‌", TAG: "ADJ"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "قدریست": [
            {ORTH: "قدری", LEMMA: "قدری", NORM: "قدری", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "قدمش": [
            {ORTH: "قدم", LEMMA: "قدم", NORM: "قدم", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "قسمتش": [
            {ORTH: "قسمت", LEMMA: "قسمت", NORM: "قسمت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "قضایاست": [
            {ORTH: "قضایا", LEMMA: "قضایا", NORM: "قضایا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "قضیه‌شان": [
            {ORTH: "قضیه‌", LEMMA: "قضیه‌", NORM: "قضیه‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "قهرمانهایشان": [
            {ORTH: "قهرمانهای", LEMMA: "قهرمانهای", NORM: "قهرمانهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "قهرمانیش": [
            {ORTH: "قهرمانی", LEMMA: "قهرمانی", NORM: "قهرمانی", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "قومت": [
            {ORTH: "قوم", LEMMA: "قوم", NORM: "قوم", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "لازمه‌اش": [
            {ORTH: "لازمه‌", LEMMA: "لازمه‌", NORM: "لازمه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "مأموریتش": [
            {ORTH: "مأموریت", LEMMA: "مأموریت", NORM: "مأموریت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مأموریتم": [
            {ORTH: "مأموریت", LEMMA: "مأموریت", NORM: "مأموریت", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "مأموریت‌اند": [
            {ORTH: "مأموریت‌", LEMMA: "مأموریت‌", NORM: "مأموریت‌", TAG: "NOUN"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "مادرانشان": [
            {ORTH: "مادران", LEMMA: "مادران", NORM: "مادران", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "مادرت": [
            {ORTH: "مادر", LEMMA: "مادر", NORM: "مادر", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "مادرش": [
            {ORTH: "مادر", LEMMA: "مادر", NORM: "مادر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مادرم": [
            {ORTH: "مادر", LEMMA: "مادر", NORM: "مادر", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "ماست": [
            {ORTH: "ما", LEMMA: "ما", NORM: "ما", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "مالی‌اش": [
            {ORTH: "مالی‌", LEMMA: "مالی‌", NORM: "مالی‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "ماهیتش": [
            {ORTH: "ماهیت", LEMMA: "ماهیت", NORM: "ماهیت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مایی": [
            {ORTH: "ما", LEMMA: "ما", NORM: "ما", TAG: "NOUN"},
            {ORTH: "یی", LEMMA: "یی", NORM: "یی", TAG: "VERB"},
        ],
        "مجازاتش": [
            {ORTH: "مجازات", LEMMA: "مجازات", NORM: "مجازات", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مجبورند": [
            {ORTH: "مجبور", LEMMA: "مجبور", NORM: "مجبور", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "محتاجند": [
            {ORTH: "محتاج", LEMMA: "محتاج", NORM: "محتاج", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "محرمم": [
            {ORTH: "محرم", LEMMA: "محرم", NORM: "محرم", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "SCONJ"},
        ],
        "محلش": [
            {ORTH: "محل", LEMMA: "محل", NORM: "محل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مخالفند": [
            {ORTH: "مخالف", LEMMA: "مخالف", NORM: "مخالف", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "مخدرش": [
            {ORTH: "مخدر", LEMMA: "مخدر", NORM: "مخدر", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مدتهاست": [
            {ORTH: "مدتها", LEMMA: "مدتها", NORM: "مدتها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "مدرسه‌ات": [
            {ORTH: "مدرسه", LEMMA: "مدرسه", NORM: "مدرسه", TAG: "NOUN"},
            {ORTH: "‌ات", LEMMA: "ات", NORM: "ات", TAG: "NOUN"},
        ],
        "مدرکم": [
            {ORTH: "مدرک", LEMMA: "مدرک", NORM: "مدرک", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "مدیرانش": [
            {ORTH: "مدیران", LEMMA: "مدیران", NORM: "مدیران", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مدیونم": [
            {ORTH: "مدیون", LEMMA: "مدیون", NORM: "مدیون", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "مذهبی‌اند": [
            {ORTH: "مذهبی‌", LEMMA: "مذهبی‌", NORM: "مذهبی‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "مرا": [
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
            {ORTH: "را", LEMMA: "را", NORM: "را", TAG: "PART"},
        ],
        "مرادت": [
            {ORTH: "مراد", LEMMA: "مراد", NORM: "مراد", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "مردمشان": [
            {ORTH: "مردم", LEMMA: "مردم", NORM: "مردم", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "مردمند": [
            {ORTH: "مردم", LEMMA: "مردم", NORM: "مردم", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "مردم‌اند": [
            {ORTH: "مردم‌", LEMMA: "مردم‌", NORM: "مردم‌", TAG: "NOUN"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "مرزشان": [
            {ORTH: "مرز", LEMMA: "مرز", NORM: "مرز", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "مرزهاشان": [
            {ORTH: "مرزها", LEMMA: "مرزها", NORM: "مرزها", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "مزدورش": [
            {ORTH: "مزدور", LEMMA: "مزدور", NORM: "مزدور", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مسئولیتش": [
            {ORTH: "مسئولیت", LEMMA: "مسئولیت", NORM: "مسئولیت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مسائلش": [
            {ORTH: "مسائل", LEMMA: "مسائل", NORM: "مسائل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مستحضرید": [
            {ORTH: "مستحضر", LEMMA: "مستحضر", NORM: "مستحضر", TAG: "ADJ"},
            {ORTH: "ید", LEMMA: "ید", NORM: "ید", TAG: "VERB"},
        ],
        "مسلمانم": [
            {ORTH: "مسلمان", LEMMA: "مسلمان", NORM: "مسلمان", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "مسلمانند": [
            {ORTH: "مسلمان", LEMMA: "مسلمان", NORM: "مسلمان", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "مشتریانش": [
            {ORTH: "مشتریان", LEMMA: "مشتریان", NORM: "مشتریان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مشتهایمان": [
            {ORTH: "مشتهای", LEMMA: "مشتهای", NORM: "مشتهای", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "مشخصند": [
            {ORTH: "مشخص", LEMMA: "مشخص", NORM: "مشخص", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "مشغولند": [
            {ORTH: "مشغول", LEMMA: "مشغول", NORM: "مشغول", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "مشغولیم": [
            {ORTH: "مشغول", LEMMA: "مشغول", NORM: "مشغول", TAG: "ADJ"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "مشهورش": [
            {ORTH: "مشهور", LEMMA: "مشهور", NORM: "مشهور", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مشکلاتشان": [
            {ORTH: "مشکلات", LEMMA: "مشکلات", NORM: "مشکلات", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "مشکلم": [
            {ORTH: "مشکل", LEMMA: "مشکل", NORM: "مشکل", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "مطمئنم": [
            {ORTH: "مطمئن", LEMMA: "مطمئن", NORM: "مطمئن", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "معامله‌مان": [
            {ORTH: "معامله‌", LEMMA: "معامله‌", NORM: "معامله‌", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "معتقدم": [
            {ORTH: "معتقد", LEMMA: "معتقد", NORM: "معتقد", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "معتقدند": [
            {ORTH: "معتقد", LEMMA: "معتقد", NORM: "معتقد", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "معتقدیم": [
            {ORTH: "معتقد", LEMMA: "معتقد", NORM: "معتقد", TAG: "ADJ"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "معرفی‌اش": [
            {ORTH: "معرفی‌", LEMMA: "معرفی‌", NORM: "معرفی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "معروفش": [
            {ORTH: "معروف", LEMMA: "معروف", NORM: "معروف", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "معضلاتمان": [
            {ORTH: "معضلات", LEMMA: "معضلات", NORM: "معضلات", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "معلمش": [
            {ORTH: "معلم", LEMMA: "معلم", NORM: "معلم", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "معنایش": [
            {ORTH: "معنای", LEMMA: "معنای", NORM: "معنای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مغزشان": [
            {ORTH: "مغز", LEMMA: "مغز", NORM: "مغز", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "مفیدند": [
            {ORTH: "مفید", LEMMA: "مفید", NORM: "مفید", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "مقابلش": [
            {ORTH: "مقابل", LEMMA: "مقابل", NORM: "مقابل", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مقاله‌اش": [
            {ORTH: "مقاله‌", LEMMA: "مقاله‌", NORM: "مقاله‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "مقدمش": [
            {ORTH: "مقدم", LEMMA: "مقدم", NORM: "مقدم", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مقرش": [
            {ORTH: "مقر", LEMMA: "مقر", NORM: "مقر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مقصدشان": [
            {ORTH: "مقصد", LEMMA: "مقصد", NORM: "مقصد", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "مقصرند": [
            {ORTH: "مقصر", LEMMA: "مقصر", NORM: "مقصر", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "مقصودتان": [
            {ORTH: "مقصود", LEMMA: "مقصود", NORM: "مقصود", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "ملاقاتهایش": [
            {ORTH: "ملاقاتهای", LEMMA: "ملاقاتهای", NORM: "ملاقاتهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "ممکنشان": [
            {ORTH: "ممکن", LEMMA: "ممکن", NORM: "ممکن", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "ممیزیهاست": [
            {ORTH: "ممیزیها", LEMMA: "ممیزیها", NORM: "ممیزیها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "منظورم": [
            {ORTH: "منظور", LEMMA: "منظور", NORM: "منظور", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "منی": [
            {ORTH: "من", LEMMA: "من", NORM: "من", TAG: "NOUN"},
            {ORTH: "ی", LEMMA: "ی", NORM: "ی", TAG: "VERB"},
        ],
        "منید": [
            {ORTH: "من", LEMMA: "من", NORM: "من", TAG: "NOUN"},
            {ORTH: "ید", LEMMA: "ید", NORM: "ید", TAG: "VERB"},
        ],
        "مهربانش": [
            {ORTH: "مهربان", LEMMA: "مهربان", NORM: "مهربان", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "مهم‌اند": [
            {ORTH: "مهم‌", LEMMA: "مهم‌", NORM: "مهم‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "مواجهند": [
            {ORTH: "مواجه", LEMMA: "مواجه", NORM: "مواجه", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "مواجه‌اند": [
            {ORTH: "مواجه‌", LEMMA: "مواجه‌", NORM: "مواجه‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "مواخذه‌ات": [
            {ORTH: "مواخذه", LEMMA: "مواخذه", NORM: "مواخذه", TAG: "NOUN"},
            {ORTH: "‌ات", LEMMA: "ات", NORM: "ات", TAG: "NOUN"},
        ],
        "مواضعشان": [
            {ORTH: "مواضع", LEMMA: "مواضع", NORM: "مواضع", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "مواضعمان": [
            {ORTH: "مواضع", LEMMA: "مواضع", NORM: "مواضع", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "موافقند": [
            {ORTH: "موافق", LEMMA: "موافق", NORM: "موافق", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "موجوداتش": [
            {ORTH: "موجودات", LEMMA: "موجودات", NORM: "موجودات", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "موجودند": [
            {ORTH: "موجود", LEMMA: "موجود", NORM: "موجود", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "موردش": [
            {ORTH: "مورد", LEMMA: "مورد", NORM: "مورد", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "موضعشان": [
            {ORTH: "موضع", LEMMA: "موضع", NORM: "موضع", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "موظفند": [
            {ORTH: "موظف", LEMMA: "موظف", NORM: "موظف", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "موهایش": [
            {ORTH: "موهای", LEMMA: "موهای", NORM: "موهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "موهایمان": [
            {ORTH: "موهای", LEMMA: "موهای", NORM: "موهای", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "مویم": [
            {ORTH: "مو", LEMMA: "مو", NORM: "مو", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "NOUN"},
        ],
        "ناخرسندند": [
            {ORTH: "ناخرسند", LEMMA: "ناخرسند", NORM: "ناخرسند", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "ناراحتیش": [
            {ORTH: "ناراحتی", LEMMA: "ناراحتی", NORM: "ناراحتی", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "ناراضی‌اند": [
            {ORTH: "ناراضی‌", LEMMA: "ناراضی‌", NORM: "ناراضی‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "نارواست": [
            {ORTH: "ناروا", LEMMA: "ناروا", NORM: "ناروا", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "نازش": [
            {ORTH: "ناز", LEMMA: "ناز", NORM: "ناز", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "نامش": [
            {ORTH: "نام", LEMMA: "نام", NORM: "نام", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "نامشان": [
            {ORTH: "نام", LEMMA: "نام", NORM: "نام", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نامم": [
            {ORTH: "نام", LEMMA: "نام", NORM: "نام", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "نامه‌ات": [
            {ORTH: "نامه", LEMMA: "نامه", NORM: "نامه", TAG: "NOUN"},
            {ORTH: "‌ات", LEMMA: "ات", NORM: "ات", TAG: "NOUN"},
        ],
        "نامه‌ام": [
            {ORTH: "نامه‌", LEMMA: "نامه‌", NORM: "نامه‌", TAG: "NOUN"},
            {ORTH: "ام", LEMMA: "ام", NORM: "ام", TAG: "NOUN"},
        ],
        "ناچارم": [
            {ORTH: "ناچار", LEMMA: "ناچار", NORM: "ناچار", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "نخست‌وزیری‌اش": [
            {
                ORTH: "نخست‌وزیری‌",
                LEMMA: "نخست‌وزیری‌",
                NORM: "نخست‌وزیری‌",
                TAG: "NOUN",
            },
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "نزدش": [
            {ORTH: "نزد", LEMMA: "نزد", NORM: "نزد", TAG: "ADP"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "نشانم": [
            {ORTH: "نشان", LEMMA: "نشان", NORM: "نشان", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "نظرات‌شان": [
            {ORTH: "نظرات‌", LEMMA: "نظرات‌", NORM: "نظرات‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نظرتان": [
            {ORTH: "نظر", LEMMA: "نظر", NORM: "نظر", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "نظرش": [
            {ORTH: "نظر", LEMMA: "نظر", NORM: "نظر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "نظرشان": [
            {ORTH: "نظر", LEMMA: "نظر", NORM: "نظر", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نظرم": [
            {ORTH: "نظر", LEMMA: "نظر", NORM: "نظر", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "نظرهایشان": [
            {ORTH: "نظرهای", LEMMA: "نظرهای", NORM: "نظرهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نفاقش": [
            {ORTH: "نفاق", LEMMA: "نفاق", NORM: "نفاق", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "نفرند": [
            {ORTH: "نفر", LEMMA: "نفر", NORM: "نفر", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "نفوذیند": [
            {ORTH: "نفوذی", LEMMA: "نفوذی", NORM: "نفوذی", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "نقطه‌نظراتتان": [
            {ORTH: "نقطه‌نظرات", LEMMA: "نقطه‌نظرات", NORM: "نقطه‌نظرات", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "نمایشی‌مان": [
            {ORTH: "نمایشی‌", LEMMA: "نمایشی‌", NORM: "نمایشی‌", TAG: "ADJ"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "نمایندگی‌شان": [
            {ORTH: "نمایندگی‌", LEMMA: "نمایندگی‌", NORM: "نمایندگی‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نمونه‌اش": [
            {ORTH: "نمونه‌", LEMMA: "نمونه‌", NORM: "نمونه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "نمی‌پذیرندش": [
            {ORTH: "نمی‌پذیرند", LEMMA: "نمی‌پذیرند", NORM: "نمی‌پذیرند", TAG: "VERB"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "نوآوری‌اش": [
            {ORTH: "نوآوری‌", LEMMA: "نوآوری‌", NORM: "نوآوری‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "نوشته‌هایشان": [
            {ORTH: "نوشته‌های", LEMMA: "نوشته‌های", NORM: "نوشته‌های", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نوشته‌هایم": [
            {ORTH: "نوشته‌ها", LEMMA: "نوشته‌ها", NORM: "نوشته‌ها", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "NOUN"},
        ],
        "نکردنشان": [
            {ORTH: "نکردن", LEMMA: "نکردن", NORM: "نکردن", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نگاهداری‌شان": [
            {ORTH: "نگاهداری‌", LEMMA: "نگاهداری‌", NORM: "نگاهداری‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نگاهش": [
            {ORTH: "نگاه", LEMMA: "نگاه", NORM: "نگاه", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "نگرانم": [
            {ORTH: "نگران", LEMMA: "نگران", NORM: "نگران", TAG: "ADJ"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "VERB"},
        ],
        "نگرشهایشان": [
            {ORTH: "نگرشهای", LEMMA: "نگرشهای", NORM: "نگرشهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "نیازمندند": [
            {ORTH: "نیازمند", LEMMA: "نیازمند", NORM: "نیازمند", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "هدفش": [
            {ORTH: "هدف", LEMMA: "هدف", NORM: "هدف", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "همانست": [
            {ORTH: "همان", LEMMA: "همان", NORM: "همان", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "همراهش": [
            {ORTH: "همراه", LEMMA: "همراه", NORM: "همراه", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "همسرتان": [
            {ORTH: "همسر", LEMMA: "همسر", NORM: "همسر", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "همسرش": [
            {ORTH: "همسر", LEMMA: "همسر", NORM: "همسر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "همسرم": [
            {ORTH: "همسر", LEMMA: "همسر", NORM: "همسر", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "همفکرانش": [
            {ORTH: "همفکران", LEMMA: "همفکران", NORM: "همفکران", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "همه‌اش": [
            {ORTH: "همه‌", LEMMA: "همه‌", NORM: "همه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "همه‌شان": [
            {ORTH: "همه‌", LEMMA: "همه‌", NORM: "همه‌", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "همکارانش": [
            {ORTH: "همکاران", LEMMA: "همکاران", NORM: "همکاران", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "هم‌نظریم": [
            {ORTH: "هم‌نظر", LEMMA: "هم‌نظر", NORM: "هم‌نظر", TAG: "ADJ"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "VERB"},
        ],
        "هنرش": [
            {ORTH: "هنر", LEMMA: "هنر", NORM: "هنر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "هواست": [
            {ORTH: "هوا", LEMMA: "هوا", NORM: "هوا", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "هویتش": [
            {ORTH: "هویت", LEMMA: "هویت", NORM: "هویت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "وابسته‌اند": [
            {ORTH: "وابسته‌", LEMMA: "وابسته‌", NORM: "وابسته‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "واقفند": [
            {ORTH: "واقف", LEMMA: "واقف", NORM: "واقف", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "والدینشان": [
            {ORTH: "والدین", LEMMA: "والدین", NORM: "والدین", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "وجدان‌تان": [
            {ORTH: "وجدان‌", LEMMA: "وجدان‌", NORM: "وجدان‌", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "وجودشان": [
            {ORTH: "وجود", LEMMA: "وجود", NORM: "وجود", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "وطنم": [
            {ORTH: "وطن", LEMMA: "وطن", NORM: "وطن", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "وعده‌اش": [
            {ORTH: "وعده‌", LEMMA: "وعده‌", NORM: "وعده‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "وقتمان": [
            {ORTH: "وقت", LEMMA: "وقت", NORM: "وقت", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "ولادتش": [
            {ORTH: "ولادت", LEMMA: "ولادت", NORM: "ولادت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پایانش": [
            {ORTH: "پایان", LEMMA: "پایان", NORM: "پایان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پایش": [
            {ORTH: "پای", LEMMA: "پای", NORM: "پای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پایین‌ترند": [
            {ORTH: "پایین‌تر", LEMMA: "پایین‌تر", NORM: "پایین‌تر", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "پدرت": [
            {ORTH: "پدر", LEMMA: "پدر", NORM: "پدر", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "پدرش": [
            {ORTH: "پدر", LEMMA: "پدر", NORM: "پدر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پدرشان": [
            {ORTH: "پدر", LEMMA: "پدر", NORM: "پدر", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "پدرم": [
            {ORTH: "پدر", LEMMA: "پدر", NORM: "پدر", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "پربارش": [
            {ORTH: "پربار", LEMMA: "پربار", NORM: "پربار", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پروردگارت": [
            {ORTH: "پروردگار", LEMMA: "پروردگار", NORM: "پروردگار", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "پسرتان": [
            {ORTH: "پسر", LEMMA: "پسر", NORM: "پسر", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "پسرش": [
            {ORTH: "پسر", LEMMA: "پسر", NORM: "پسر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پسرعمویش": [
            {ORTH: "پسرعموی", LEMMA: "پسرعموی", NORM: "پسرعموی", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پسر‌عمویت": [
            {ORTH: "پسر‌عموی", LEMMA: "پسر‌عموی", NORM: "پسر‌عموی", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "پشتش": [
            {ORTH: "پشت", LEMMA: "پشت", NORM: "پشت", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پشیمونی": [
            {ORTH: "پشیمون", LEMMA: "پشیمون", NORM: "پشیمون", TAG: "ADJ"},
            {ORTH: "ی", LEMMA: "ی", NORM: "ی", TAG: "VERB"},
        ],
        "پولش": [
            {ORTH: "پول", LEMMA: "پول", NORM: "پول", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پژوهش‌هایش": [
            {ORTH: "پژوهش‌های", LEMMA: "پژوهش‌های", NORM: "پژوهش‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پیامبرش": [
            {ORTH: "پیامبر", LEMMA: "پیامبر", NORM: "پیامبر", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پیامبری": [
            {ORTH: "پیامبر", LEMMA: "پیامبر", NORM: "پیامبر", TAG: "NOUN"},
            {ORTH: "ی", LEMMA: "ی", NORM: "ی", TAG: "VERB"},
        ],
        "پیامش": [
            {ORTH: "پیام", LEMMA: "پیام", NORM: "پیام", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پیداست": [
            {ORTH: "پیدا", LEMMA: "پیدا", NORM: "پیدا", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "پیراهنش": [
            {ORTH: "پیراهن", LEMMA: "پیراهن", NORM: "پیراهن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پیروانش": [
            {ORTH: "پیروان", LEMMA: "پیروان", NORM: "پیروان", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "پیشانی‌اش": [
            {ORTH: "پیشانی‌", LEMMA: "پیشانی‌", NORM: "پیشانی‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "پیمانت": [
            {ORTH: "پیمان", LEMMA: "پیمان", NORM: "پیمان", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "پیوندشان": [
            {ORTH: "پیوند", LEMMA: "پیوند", NORM: "پیوند", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "چاپش": [
            {ORTH: "چاپ", LEMMA: "چاپ", NORM: "چاپ", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "چت": [
            {ORTH: "چ", LEMMA: "چ", NORM: "چ", TAG: "ADV"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "چته": [
            {ORTH: "چ", LEMMA: "چ", NORM: "چ", TAG: "ADV"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
            {ORTH: "ه", LEMMA: "ه", NORM: "ه", TAG: "VERB"},
        ],
        "چرخ‌هایش": [
            {ORTH: "چرخ‌های", LEMMA: "چرخ‌های", NORM: "چرخ‌های", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "چشمم": [
            {ORTH: "چشم", LEMMA: "چشم", NORM: "چشم", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "چشمهایش": [
            {ORTH: "چشمهای", LEMMA: "چشمهای", NORM: "چشمهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "چشمهایشان": [
            {ORTH: "چشمهای", LEMMA: "چشمهای", NORM: "چشمهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "چمنم": [
            {ORTH: "چمن", LEMMA: "چمن", NORM: "چمن", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "چهره‌اش": [
            {ORTH: "چهره‌", LEMMA: "چهره‌", NORM: "چهره‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "چکاره‌اند": [
            {ORTH: "چکاره‌", LEMMA: "چکاره‌", NORM: "چکاره‌", TAG: "ADV"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "چیزهاست": [
            {ORTH: "چیزها", LEMMA: "چیزها", NORM: "چیزها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "چیزهایش": [
            {ORTH: "چیزهای", LEMMA: "چیزهای", NORM: "چیزهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "چیزیست": [
            {ORTH: "چیزی", LEMMA: "چیزی", NORM: "چیزی", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "چیست": [
            {ORTH: "چی", LEMMA: "چی", NORM: "چی", TAG: "ADV"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "کارش": [
            {ORTH: "کار", LEMMA: "کار", NORM: "کار", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "کارشان": [
            {ORTH: "کار", LEMMA: "کار", NORM: "کار", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "کارم": [
            {ORTH: "کار", LEMMA: "کار", NORM: "کار", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "کارند": [
            {ORTH: "کار", LEMMA: "کار", NORM: "کار", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "کارهایم": [
            {ORTH: "کارها", LEMMA: "کارها", NORM: "کارها", TAG: "NOUN"},
            {ORTH: "یم", LEMMA: "یم", NORM: "یم", TAG: "NOUN"},
        ],
        "کافیست": [
            {ORTH: "کافی", LEMMA: "کافی", NORM: "کافی", TAG: "ADJ"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "کتابخانه‌اش": [
            {ORTH: "کتابخانه‌", LEMMA: "کتابخانه‌", NORM: "کتابخانه‌", TAG: "NOUN"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "کتابش": [
            {ORTH: "کتاب", LEMMA: "کتاب", NORM: "کتاب", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "کتابهاشان": [
            {ORTH: "کتابها", LEMMA: "کتابها", NORM: "کتابها", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "کجاست": [
            {ORTH: "کجا", LEMMA: "کجا", NORM: "کجا", TAG: "ADV"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "کدورتهایشان": [
            {ORTH: "کدورتهای", LEMMA: "کدورتهای", NORM: "کدورتهای", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "کردنش": [
            {ORTH: "کردن", LEMMA: "کردن", NORM: "کردن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "کرم‌خورده‌اش": [
            {ORTH: "کرم‌خورده‌", LEMMA: "کرم‌خورده‌", NORM: "کرم‌خورده‌", TAG: "ADJ"},
            {ORTH: "اش", LEMMA: "اش", NORM: "اش", TAG: "NOUN"},
        ],
        "کشش": [
            {ORTH: "کش", LEMMA: "کش", NORM: "کش", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "کشورش": [
            {ORTH: "کشور", LEMMA: "کشور", NORM: "کشور", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "کشورشان": [
            {ORTH: "کشور", LEMMA: "کشور", NORM: "کشور", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "کشورمان": [
            {ORTH: "کشور", LEMMA: "کشور", NORM: "کشور", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "کشورهاست": [
            {ORTH: "کشورها", LEMMA: "کشورها", NORM: "کشورها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "کلیشه‌هاست": [
            {ORTH: "کلیشه‌ها", LEMMA: "کلیشه‌ها", NORM: "کلیشه‌ها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "کمبودهاست": [
            {ORTH: "کمبودها", LEMMA: "کمبودها", NORM: "کمبودها", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "کمتره": [
            {ORTH: "کمتر", LEMMA: "کمتر", NORM: "کمتر", TAG: "ADJ"},
            {ORTH: "ه", LEMMA: "ه", NORM: "ه", TAG: "VERB"},
        ],
        "کمکم": [
            {ORTH: "کمک", LEMMA: "کمک", NORM: "کمک", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "کنارش": [
            {ORTH: "کنار", LEMMA: "کنار", NORM: "کنار", TAG: "ADP"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "کودکانشان": [
            {ORTH: "کودکان", LEMMA: "کودکان", NORM: "کودکان", TAG: "NOUN"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "کوچکش": [
            {ORTH: "کوچک", LEMMA: "کوچک", NORM: "کوچک", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "کیست": [
            {ORTH: "کی", LEMMA: "کی", NORM: "کی", TAG: "NOUN"},
            {ORTH: "ست", LEMMA: "ست", NORM: "ست", TAG: "VERB"},
        ],
        "کیفش": [
            {ORTH: "کیف", LEMMA: "کیف", NORM: "کیف", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "گذشته‌اند": [
            {ORTH: "گذشته‌", LEMMA: "گذشته‌", NORM: "گذشته‌", TAG: "ADJ"},
            {ORTH: "اند", LEMMA: "اند", NORM: "اند", TAG: "VERB"},
        ],
        "گرانقدرش": [
            {ORTH: "گرانقدر", LEMMA: "گرانقدر", NORM: "گرانقدر", TAG: "ADJ"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "گرانقدرشان": [
            {ORTH: "گرانقدر", LEMMA: "گرانقدر", NORM: "گرانقدر", TAG: "ADJ"},
            {ORTH: "شان", LEMMA: "شان", NORM: "شان", TAG: "NOUN"},
        ],
        "گردنتان": [
            {ORTH: "گردن", LEMMA: "گردن", NORM: "گردن", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "گردنش": [
            {ORTH: "گردن", LEMMA: "گردن", NORM: "گردن", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "گرفتارند": [
            {ORTH: "گرفتار", LEMMA: "گرفتار", NORM: "گرفتار", TAG: "ADJ"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "گرفتنت": [
            {ORTH: "گرفتن", LEMMA: "گرفتن", NORM: "گرفتن", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "گروهند": [
            {ORTH: "گروه", LEMMA: "گروه", NORM: "گروه", TAG: "NOUN"},
            {ORTH: "ند", LEMMA: "ند", NORM: "ند", TAG: "VERB"},
        ],
        "گروگانهایش": [
            {ORTH: "گروگانهای", LEMMA: "گروگانهای", NORM: "گروگانهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "گریمش": [
            {ORTH: "گریم", LEMMA: "گریم", NORM: "گریم", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "گفتارمان": [
            {ORTH: "گفتار", LEMMA: "گفتار", NORM: "گفتار", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "گلهایش": [
            {ORTH: "گلهای", LEMMA: "گلهای", NORM: "گلهای", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "گلویش": [
            {ORTH: "گلوی", LEMMA: "گلوی", NORM: "گلوی", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "گناهت": [
            {ORTH: "گناه", LEMMA: "گناه", NORM: "گناه", TAG: "NOUN"},
            {ORTH: "ت", LEMMA: "ت", NORM: "ت", TAG: "NOUN"},
        ],
        "گوشش": [
            {ORTH: "گوش", LEMMA: "گوش", NORM: "گوش", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "گوشم": [
            {ORTH: "گوش", LEMMA: "گوش", NORM: "گوش", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "گولش": [
            {ORTH: "گول", LEMMA: "گول", NORM: "گول", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
        "یادتان": [
            {ORTH: "یاد", LEMMA: "یاد", NORM: "یاد", TAG: "NOUN"},
            {ORTH: "تان", LEMMA: "تان", NORM: "تان", TAG: "NOUN"},
        ],
        "یادم": [
            {ORTH: "یاد", LEMMA: "یاد", NORM: "یاد", TAG: "NOUN"},
            {ORTH: "م", LEMMA: "م", NORM: "م", TAG: "NOUN"},
        ],
        "یادمان": [
            {ORTH: "یاد", LEMMA: "یاد", NORM: "یاد", TAG: "NOUN"},
            {ORTH: "مان", LEMMA: "مان", NORM: "مان", TAG: "NOUN"},
        ],
        "یارانش": [
            {ORTH: "یاران", LEMMA: "یاران", NORM: "یاران", TAG: "NOUN"},
            {ORTH: "ش", LEMMA: "ش", NORM: "ش", TAG: "NOUN"},
        ],
    }
)
TOKENIZER_EXCEPTIONS = _exc
