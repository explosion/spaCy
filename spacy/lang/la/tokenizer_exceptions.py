from ...symbols import ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

## TODO: Look into systematically handling u/v
_exc = {
    "mecum": [{ORTH: "me"}, {ORTH: "cum"}],
    "tecum": [{ORTH: "te"}, {ORTH: "cum"}],
    "nobiscum": [{ORTH: "nobis"}, {ORTH: "cum"}],
    "vobiscum": [{ORTH: "vobis"}, {ORTH: "cum"}],
    "uobiscum": [{ORTH: "uobis"}, {ORTH: "cum"}],
}

_abbrev_exc = """A. A.D. Aa. Aaa. Acc. Agr. Ap. Apr. April. A.U.C. Aug. C. Caes. Caess. Cc. Cn. Coll. Cons. Conss. Cos. Coss. D. D.N. Dat. Dd. Dec. Decemb. Decembr. F. Feb. Febr. Februar. Ian. Id. Imp. Impp. Imppp. Iul. Iun. K. Kal. L. M'. M. Mai. Mam. Mar. Mart. Med. N. Nn. Nob. Non. Nov. Novemb. Oct. Octob. Opet. Ord. P. Paul. Pf. Pl. Plur. Post. Pp. Prid. Pro. Procos. Q. Quint. S. S.C. Scr. Sept. Septemb. Ser. Sert. Sex. Sext. St. Sta. Suff. T. Ti. Trib. V. Vol. Vop. Vv.""".split()

_abbrev_exc += [item.lower() for item in _abbrev_exc]
_abbrev_exc += [item.upper() for item in _abbrev_exc]
_abbrev_exc += [item.replace("v", "u").replace("V", "U") for item in _abbrev_exc]

_abbrev_exc += ["d.N."]

for orth in set(_abbrev_exc):
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
