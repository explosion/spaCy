from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...symbols import ORTH, NORM
from ...util import update_exc

_exc = {}

for token in ["᾽Απ'", "᾽ΑΠ'", "ἀφ'", "᾽Αφ", "ἀπὸ"]:
    _exc[token] = [{ORTH: token, NORM: "από"}]

for token in ["᾽Αλλ'", "ἀλλ'", "ἀλλὰ"]:
    _exc[token] = [{ORTH: token, NORM: "ἀλλά"}]

for token in ["παρ'", "Παρ'", "παρὰ", "παρ"]:
    _exc[token] = [{ORTH: token, NORM: "παρά"}]

for token in ["καθ'", "Καθ'", "κατ'", "Κατ'", "κατὰ"]:
    _exc[token] = [{ORTH: token, NORM: "κατά"}]

for token in ["Ἐπ'", "ἐπ'", "ἐπὶ", "Εφ'", "εφ'"]:
    _exc[token] = [{ORTH: token, NORM: "επί"}]

for token in ["Δι'", "δι'", "διὰ"]:
    _exc[token] = [{ORTH: token, NORM: "διά"}]

for token in ["Ὑπ'", "ὑπ'", "ὑφ'"]:
    _exc[token] = [{ORTH: token, NORM: "ὑπό"}]

for token in ["Μετ'", "μετ'", "μεθ'", "μετὰ"]:
    _exc[token] = [{ORTH: token, NORM: "μετά"}]

for token in ["Μ'", "μ'", "μέ", "μὲ"]:
    _exc[token] = [{ORTH: token, NORM: "με"}]

for token in ["Σ'", "σ'", "σέ", "σὲ"]:
    _exc[token] = [{ORTH: token, NORM: "σε"}]

for token in ["Τ'", "τ'", "τέ", "τὲ"]:
    _exc[token] = [{ORTH: token, NORM: "τε"}]

for token in ["Δ'", "δ'", "δὲ"]:
    _exc[token] = [{ORTH: token, NORM: "δέ"}]


_other_exc = {
    "μὲν": [{ORTH: "μὲν", NORM: "μέν"}],
    "μὴν": [{ORTH: "μὴν", NORM: "μήν"}],
    "τὴν": [{ORTH: "τὴν", NORM: "τήν"}],
    "τὸν": [{ORTH: "τὸν", NORM: "τόν"}],
    "καὶ": [{ORTH: "καὶ", NORM: "καί"}],
    "καὐτός": [{ORTH: "κ", NORM: "καί"}, {ORTH: "αὐτός"}],
    "καὐτὸς": [{ORTH: "κ", NORM: "καί"}, {ORTH: "αὐτὸς", NORM: "αὐτός"}],
    "κοὐ": [{ORTH: "κ", NORM: "καί"}, {ORTH: "οὐ"}],
    "χἡ": [{ORTH: "χ", NORM: "καί"}, {ORTH: "ἡ"}],
    "χοἱ": [{ORTH: "χ", NORM: "καί"}, {ORTH: "οἱ"}],
    "χἱκετεύετε": [{ORTH: "χ", NORM: "καί"}, {ORTH: "ἱκετεύετε"}],
    "κἀν": [{ORTH: "κ", NORM: "καί"}, {ORTH: "ἀν", NORM: "ἐν"}],
    "κἀγὼ": [{ORTH: "κἀ", NORM: "καί"}, {ORTH: "γὼ", NORM: "ἐγώ"}],
    "κἀγώ": [{ORTH: "κἀ", NORM: "καί"}, {ORTH: "γώ", NORM: "ἐγώ"}],
    "ἁγώ": [{ORTH: "ἁ", NORM: "ἃ"}, {ORTH: "γώ", NORM: "ἐγώ"}],
    "ἁγὼ": [{ORTH: "ἁ", NORM: "ἃ"}, {ORTH: "γὼ", NORM: "ἐγώ"}],
    "ἐγᾦδα": [{ORTH: "ἐγ", NORM: "ἐγώ"}, {ORTH: "ᾦδα", NORM: "οἶδα"}],
    "ἐγᾦμαι": [{ORTH: "ἐγ", NORM: "ἐγώ"}, {ORTH: "ᾦμαι", NORM: "οἶμαι"}],
    "κἀς": [{ORTH: "κ", NORM: "καί"}, {ORTH: "ἀς", NORM: "ἐς"}],
    "κᾆτα": [{ORTH: "κ", NORM: "καί"}, {ORTH: "ᾆτα", NORM: "εἶτα"}],
    "κεἰ": [{ORTH: "κ", NORM: "καί"}, {ORTH: "εἰ"}],
    "κεἰς": [{ORTH: "κ", NORM: "καί"}, {ORTH: "εἰς"}],
    "χὤτε": [{ORTH: "χ", NORM: "καί"}, {ORTH: "ὤτε", NORM: "ὅτε"}],
    "χὤπως": [{ORTH: "χ", NORM: "καί"}, {ORTH: "ὤπως", NORM: "ὅπως"}],
    "χὤτι": [{ORTH: "χ", NORM: "καί"}, {ORTH: "ὤτι", NORM: "ὅτι"}],
    "χὤταν": [{ORTH: "χ", NORM: "καί"}, {ORTH: "ὤταν", NORM: "ὅταν"}],
    "οὑμός": [{ORTH: "οὑ", NORM: "ὁ"}, {ORTH: "μός", NORM: "ἐμός"}],
    "οὑμὸς": [{ORTH: "οὑ", NORM: "ὁ"}, {ORTH: "μὸς", NORM: "ἐμός"}],
    "οὑμοί": [{ORTH: "οὑ", NORM: "οἱ"}, {ORTH: "μοί", NORM: "ἐμoί"}],
    "οὑμοὶ": [{ORTH: "οὑ", NORM: "οἱ"}, {ORTH: "μοὶ", NORM: "ἐμoί"}],
    "σοὔστι": [{ORTH: "σοὔ", NORM: "σοί"}, {ORTH: "στι", NORM: "ἐστι"}],
    "σοὐστί": [{ORTH: "σοὐ", NORM: "σοί"}, {ORTH: "στί", NORM: "ἐστί"}],
    "σοὐστὶ": [{ORTH: "σοὐ", NORM: "σοί"}, {ORTH: "στὶ", NORM: "ἐστί"}],
    "μοὖστι": [{ORTH: "μοὖ", NORM: "μοί"}, {ORTH: "στι", NORM: "ἐστι"}],
    "μοὔστι": [{ORTH: "μοὔ", NORM: "μοί"}, {ORTH: "στι", NORM: "ἐστι"}],
    "τοὔνομα": [{ORTH: "τοὔ", NORM: "τό"}, {ORTH: "νομα", NORM: "ὄνομα"}],
    "οὑν": [{ORTH: "οὑ", NORM: "ὁ"}, {ORTH: "ν", NORM: "ἐν"}],
    "ὦνερ": [{ORTH: "ὦ", NORM: "ὦ"}, {ORTH: "νερ", NORM: "ἄνερ"}],
    "ὦνδρες": [{ORTH: "ὦ", NORM: "ὦ"}, {ORTH: "νδρες", NORM: "ἄνδρες"}],
    "προὔχων": [{ORTH: "προὔ", NORM: "πρό"}, {ORTH: "χων", NORM: "ἔχων"}],
    "προὔχοντα": [{ORTH: "προὔ", NORM: "πρό"}, {ORTH: "χοντα", NORM: "ἔχοντα"}],
    "ὥνεκα": [{ORTH: "ὥ", NORM: "οὗ"}, {ORTH: "νεκα", NORM: "ἕνεκα"}],
    "θοἰμάτιον": [{ORTH: "θο", NORM: "τό"}, {ORTH: "ἰμάτιον"}],
    "ὥνεκα": [{ORTH: "ὥ", NORM: "οὗ"}, {ORTH: "νεκα", NORM: "ἕνεκα"}],
    "τὠληθές": [{ORTH: "τὠ", NORM: "τὸ"}, {ORTH: "ληθές", NORM: "ἀληθές"}],
    "θἡμέρᾳ": [{ORTH: "θ", NORM: "τῇ"}, {ORTH: "ἡμέρᾳ"}],
    "ἅνθρωπος": [{ORTH: "ἅ", NORM: "ὁ"}, {ORTH: "νθρωπος", NORM: "ἄνθρωπος"}],
    "τἄλλα": [{ORTH: "τ", NORM: "τὰ"}, {ORTH: "ἄλλα"}],
    "τἆλλα": [{ORTH: "τἆ", NORM: "τὰ"}, {ORTH: "λλα", NORM: "ἄλλα"}],
    "ἁνήρ": [{ORTH: "ἁ", NORM: "ὁ"}, {ORTH: "νήρ", NORM: "ἀνήρ"}],
    "ἁνὴρ": [{ORTH: "ἁ", NORM: "ὁ"}, {ORTH: "νὴρ", NORM: "ἀνήρ"}],
    "ἅνδρες": [{ORTH: "ἅ", NORM: "οἱ"}, {ORTH: "νδρες", NORM: "ἄνδρες"}],
    "ἁγαθαί": [{ORTH: "ἁ", NORM: "αἱ"}, {ORTH: "γαθαί", NORM: "ἀγαθαί"}],
    "ἁγαθαὶ": [{ORTH: "ἁ", NORM: "αἱ"}, {ORTH: "γαθαὶ", NORM: "ἀγαθαί"}],
    "ἁλήθεια": [{ORTH: "ἁ", NORM: "ἡ"}, {ORTH: "λήθεια", NORM: "ἀλήθεια"}],
    "τἀνδρός": [{ORTH: "τ", NORM: "τοῦ"}, {ORTH: "ἀνδρός"}],
    "τἀνδρὸς": [{ORTH: "τ", NORM: "τοῦ"}, {ORTH: "ἀνδρὸς", NORM: "ἀνδρός"}],
    "τἀνδρί": [{ORTH: "τ", NORM: "τῷ"}, {ORTH: "ἀνδρί"}],
    "τἀνδρὶ": [{ORTH: "τ", NORM: "τῷ"}, {ORTH: "ἀνδρὶ", NORM: "ἀνδρί"}],
    "αὑτός": [{ORTH: "αὑ", NORM: "ὁ"}, {ORTH: "τός", NORM: "αὐτός"}],
    "αὑτὸς": [{ORTH: "αὑ", NORM: "ὁ"}, {ORTH: "τὸς", NORM: "αὐτός"}],
    "ταὐτοῦ": [{ORTH: "τ", NORM: "τοῦ"}, {ORTH: "αὐτοῦ"}],
}

_exc.update(_other_exc)

_exc_data = {}

_exc.update(_exc_data)

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
