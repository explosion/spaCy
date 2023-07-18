"""
References:
    https://slovored.com/bg/abbr/grammar/ - Additional refs for abbreviations
    (countries, occupations, fields of studies and more).
"""

from ...symbols import NORM, ORTH

_exc = {}

# measurements
for abbr in [
    {ORTH: "м", NORM: "метър"},
    {ORTH: "мм", NORM: "милиметър"},
    {ORTH: "см", NORM: "сантиметър"},
    {ORTH: "дм", NORM: "дециметър"},
    {ORTH: "км", NORM: "километър"},
    {ORTH: "кг", NORM: "килограм"},
    {ORTH: "мг", NORM: "милиграм"},
    {ORTH: "г", NORM: "грам"},
    {ORTH: "т", NORM: "тон"},
    {ORTH: "хл", NORM: "хектолиър"},
    {ORTH: "дкл", NORM: "декалитър"},
    {ORTH: "л", NORM: "литър"},
]:
    _exc[abbr[ORTH]] = [abbr]

# line abbreviations
for abbr in [
    {ORTH: "г-жа", NORM: "госпожа"},
    {ORTH: "г-н", NORM: "господин"},
    {ORTH: "г-ца", NORM: "госпожица"},
    {ORTH: "д-р", NORM: "доктор"},
    {ORTH: "о-в", NORM: "остров"},
    {ORTH: "п-в", NORM: "полуостров"},
    {ORTH: "с-у", NORM: "срещу"},
    {ORTH: "в-у", NORM: "върху"},
    {ORTH: "м-у", NORM: "между"},
]:
    _exc[abbr[ORTH]] = [abbr]

# foreign language related abbreviations
for abbr in [
    {ORTH: "англ.", NORM: "английски"},
    {ORTH: "ан.", NORM: "английски термин"},
    {ORTH: "араб.", NORM: "арабски"},
    {ORTH: "афр.", NORM: "африкански"},
    {ORTH: "гр.", NORM: "гръцки"},
    {ORTH: "лат.", NORM: "латински"},
    {ORTH: "рим.", NORM: "римски"},
    {ORTH: "старогр.", NORM: "старогръцки"},
    {ORTH: "староевр.", NORM: "староеврейски"},
    {ORTH: "фр.", NORM: "френски"},
    {ORTH: "хол.", NORM: "холандски"},
    {ORTH: "швед.", NORM: "шведски"},
    {ORTH: "шотл.", NORM: "шотландски"},
    {ORTH: "яп.", NORM: "японски"},
]:
    _exc[abbr[ORTH]] = [abbr]

# profession and academic titles abbreviations
for abbr in [
    {ORTH: "акад.", NORM: "академик"},
    {ORTH: "арх.", NORM: "архитект"},
    {ORTH: "инж.", NORM: "инженер"},
    {ORTH: "канц.", NORM: "канцлер"},
    {ORTH: "проф.", NORM: "професор"},
    {ORTH: "св.", NORM: "свети"},
]:
    _exc[abbr[ORTH]] = [abbr]

# fields of studies
for abbr in [
    {ORTH: "агр.", NORM: "агрономия"},
    {ORTH: "ав.", NORM: "авиация"},
    {ORTH: "агр.", NORM: "агрономия"},
    {ORTH: "археол.", NORM: "археология"},
    {ORTH: "астр.", NORM: "астрономия"},
    {ORTH: "геод.", NORM: "геодезия"},
    {ORTH: "геол.", NORM: "геология"},
    {ORTH: "геом.", NORM: "геометрия"},
    {ORTH: "гимн.", NORM: "гимнастика"},
    {ORTH: "грам.", NORM: "граматика"},
    {ORTH: "жур.", NORM: "журналистика"},
    {ORTH: "журн.", NORM: "журналистика"},
    {ORTH: "зем.", NORM: "земеделие"},
    {ORTH: "икон.", NORM: "икономика"},
    {ORTH: "лит.", NORM: "литература"},
    {ORTH: "мат.", NORM: "математика"},
    {ORTH: "мед.", NORM: "медицина"},
    {ORTH: "муз.", NORM: "музика"},
    {ORTH: "печ.", NORM: "печатарство"},
    {ORTH: "пол.", NORM: "политика"},
    {ORTH: "псих.", NORM: "психология"},
    {ORTH: "соц.", NORM: "социология"},
    {ORTH: "стат.", NORM: "статистика"},
    {ORTH: "стил.", NORM: "стилистика"},
    {ORTH: "топогр.", NORM: "топография"},
    {ORTH: "търг.", NORM: "търговия"},
    {ORTH: "фарм.", NORM: "фармацевтика"},
    {ORTH: "фехт.", NORM: "фехтовка"},
    {ORTH: "физиол.", NORM: "физиология"},
    {ORTH: "физ.", NORM: "физика"},
    {ORTH: "фил.", NORM: "философия"},
    {ORTH: "фин.", NORM: "финанси"},
    {ORTH: "фолкл.", NORM: "фолклор"},
    {ORTH: "фон.", NORM: "фонетика"},
    {ORTH: "фот.", NORM: "фотография"},
    {ORTH: "футб.", NORM: "футбол"},
    {ORTH: "хим.", NORM: "химия"},
    {ORTH: "хир.", NORM: "хирургия"},
    {ORTH: "ел.", NORM: "електротехника"},
]:
    _exc[abbr[ORTH]] = [abbr]

for abbr in [
    {ORTH: "ал.", NORM: "алинея"},
    {ORTH: "авт.", NORM: "автоматично"},
    {ORTH: "адм.", NORM: "администрация"},
    {ORTH: "арт.", NORM: "артилерия"},
    {ORTH: "бл.", NORM: "блок"},
    {ORTH: "бр.", NORM: "брой"},
    {ORTH: "бул.", NORM: "булевард"},
    {ORTH: "букв.", NORM: "буквално"},
    {ORTH: "в.", NORM: "век"},
    {ORTH: "вр.", NORM: "време"},
    {ORTH: "вм.", NORM: "вместо"},
    {ORTH: "воен.", NORM: "военен термин"},
    {ORTH: "г.", NORM: "година"},
    {ORTH: "гр.", NORM: "град"},
    {ORTH: "гл.", NORM: "глагол"},
    {ORTH: "др.", NORM: "други"},
    {ORTH: "ез.", NORM: "езеро"},
    {ORTH: "ж.р.", NORM: "женски род"},
    {ORTH: "жп.", NORM: "железопът"},
    {ORTH: "застр.", NORM: "застрахователно дело"},
    {ORTH: "знач.", NORM: "значение"},
    {ORTH: "и др.", NORM: "и други"},
    {ORTH: "и под.", NORM: "и подобни"},
    {ORTH: "и пр.", NORM: "и прочие"},
    {ORTH: "изр.", NORM: "изречение"},
    {ORTH: "изт.", NORM: "източен"},
    {ORTH: "конкр.", NORM: "конкретно"},
    {ORTH: "лв.", NORM: "лев"},
    {ORTH: "л.", NORM: "лице"},
    {ORTH: "м.р.", NORM: "мъжки род"},
    {ORTH: "мин.вр.", NORM: "минало време"},
    {ORTH: "мн.ч.", NORM: "множествено число"},
    {ORTH: "напр.", NORM: "например"},
    {ORTH: "нар.", NORM: "наречие"},
    {ORTH: "науч.", NORM: "научен термин"},
    {ORTH: "непр.", NORM: "неправилно"},
    {ORTH: "обик.", NORM: "обикновено"},
    {ORTH: "опред.", NORM: "определение"},
    {ORTH: "особ.", NORM: "особено"},
    {ORTH: "ост.", NORM: "остаряло"},
    {ORTH: "относ.", NORM: "относително"},
    {ORTH: "отр.", NORM: "отрицателно"},
    {ORTH: "пл.", NORM: "площад"},
    {ORTH: "пад.", NORM: "падеж"},
    {ORTH: "парл.", NORM: "парламентарен"},
    {ORTH: "погов.", NORM: "поговорка"},
    {ORTH: "пон.", NORM: "понякога"},
    {ORTH: "правосл.", NORM: "православен"},
    {ORTH: "прибл.", NORM: "приблизително"},
    {ORTH: "прил.", NORM: "прилагателно име"},
    {ORTH: "пр.", NORM: "прочие"},
    {ORTH: "с.", NORM: "село"},
    {ORTH: "с.р.", NORM: "среден род"},
    {ORTH: "сп.", NORM: "списание"},
    {ORTH: "стр.", NORM: "страница"},
    {ORTH: "сз.", NORM: "съюз"},
    {ORTH: "сег.", NORM: "сегашно"},
    {ORTH: "сп.", NORM: "спорт"},
    {ORTH: "срв.", NORM: "сравни"},
    {ORTH: "с.ст.", NORM: "селскостопанска техника"},
    {ORTH: "счет.", NORM: "счетоводство"},
    {ORTH: "съкр.", NORM: "съкратено"},
    {ORTH: "съобщ.", NORM: "съобщение"},
    {ORTH: "същ.", NORM: "съществително"},
    {ORTH: "текст.", NORM: "текстилен"},
    {ORTH: "телев.", NORM: "телевизия"},
    {ORTH: "тел.", NORM: "телефон"},
    {ORTH: "т.е.", NORM: "тоест"},
    {ORTH: "т.н.", NORM: "така нататък"},
    {ORTH: "т.нар.", NORM: "така наречен"},
    {ORTH: "търж.", NORM: "тържествено"},
    {ORTH: "ул.", NORM: "улица"},
    {ORTH: "уч.", NORM: "училище"},
    {ORTH: "унив.", NORM: "университет"},
    {ORTH: "харт.", NORM: "хартия"},
    {ORTH: "хидр.", NORM: "хидравлика"},
    {ORTH: "хран.", NORM: "хранителна"},
    {ORTH: "църк.", NORM: "църковен термин"},
    {ORTH: "числ.", NORM: "числително"},
    {ORTH: "чл.", NORM: "член"},
    {ORTH: "ч.", NORM: "число"},
    {ORTH: "числ.", NORM: "числително"},
    {ORTH: "шахм.", NORM: "шахмат"},
    {ORTH: "шах.", NORM: "шахмат"},
    {ORTH: "юр.", NORM: "юридически"},
]:
    _exc[abbr[ORTH]] = [abbr]

# slash abbreviations
for abbr in [
    {ORTH: "м/у", NORM: "между"},
    {ORTH: "с/у", NORM: "срещу"},
]:
    _exc[abbr[ORTH]] = [abbr]

TOKENIZER_EXCEPTIONS = _exc
