"""
Helpers for Python and platform compatibility. To distinguish them from
the builtin functions, replacement functions are suffixed with an underscore,
e.g. `unicode_`.

DOCS: https://spacy.io/api/top-level#compat
"""
import sys

from thinc.util import copy_array

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import copy_reg
except ImportError:
    import copyreg as copy_reg

try:
    from cupy.cuda.stream import Stream as CudaStream
except ImportError:
    CudaStream = None

try:
    import cupy
except ImportError:
    cupy = None

from thinc.api import Optimizer  # noqa: F401

pickle = pickle
copy_reg = copy_reg
CudaStream = CudaStream
cupy = cupy
copy_array = copy_array

is_windows = sys.platform.startswith("win")
is_linux = sys.platform.startswith("linux")
is_osx = sys.platform == "darwin"


def is_config(windows=None, linux=None, osx=None, **kwargs):
    """Check if a specific configuration of Python version and operating system
    matches the user's setup. Mostly used to display targeted error messages.

    windows (bool): spaCy is executed on Windows.
    linux (bool): spaCy is executed on Linux.
    osx (bool): spaCy is executed on OS X or macOS.
    RETURNS (bool): Whether the configuration matches the user's platform.

    DOCS: https://spacy.io/api/top-level#compat.is_config
    """
    return (
        windows in (None, is_windows)
        and linux in (None, is_linux)
        and osx in (None, is_osx)
    )
