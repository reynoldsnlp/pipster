import os
import sys

from ._version import __version__  # noqa: F401
from ._version import __version_tuple__  # noqa: F401
from .install import *  # noqa: F403

is_conda = os.path.exists(os.path.join(sys.prefix, "conda-meta"))
if is_conda:
    print(
        "WARNING: Using pip/pipster with Anaconda Python can result in a corrupted "
        "environment (especially when pip and conda are used in alternation). "
        "Use conda instead."
    )  # TODO colorize WARNING?
