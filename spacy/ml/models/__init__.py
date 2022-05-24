from .entity_linker import *  # noqa
from .multi_task import *  # noqa
from .parser import *  # noqa
from .spancat import *  # noqa
from .tagger import *  # noqa
from .textcat import *  # noqa
from .tok2vec import *  # noqa

# some models require Torch
from thinc.util import has_torch
if has_torch:
    from .coref import * #noqa
    from .span_predictor import * #noqa

