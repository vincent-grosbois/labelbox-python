"""
Module to support type checking with Python 3.7
"""

import sys

from typing import Any, List, Optional, Iterator, Union

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict
