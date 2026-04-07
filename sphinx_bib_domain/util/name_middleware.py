## name_middleware.py -*- mode: python -*-
"""


"""
# ruff.ignore.in.file
from __future__ import annotations

# Imports:
# ##-- stdlib imports
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
from asyncio import (
     create_task, gather, sleep, timeout, shield,
     to_thread, current_task, all_tasks,
     TaskGroup,
     CancelledError,
)
import asyncio
import collections
import contextlib
import datetime
import enum
import faulthandler
import functools as ftz
import hashlib
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
# ##-- end stdlib imports

import bibtexparser.model as model
from bibble.people import NameReader, NameWriter
from bibble.bidi import BidiNames

# ##-- types
# isort: off
# General
import abc
import collections.abc
import typing
import types
from typing import cast, assert_type, assert_never
from typing import Generic, NewType, Never
from typing import no_type_check, final, override, overload
# Protocols and Interfaces:
from typing import Protocol, runtime_checkable
# isort: on
# ##-- end types

# ##-- type checking
# isort: off
if typing.TYPE_CHECKING:
    from typing import Final, ClassVar, Any, Self
    from typing import Literal, LiteralString
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from jgdv import Maybe
## isort: on
# ##-- end type checking

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

class _NameReader(NameReader):

    def field_h(self, field:Field, entry:Entry) -> Result[list[Field], Exception]:
        result = []
        match self._do_split_authors:
            case True:
                authors = self._split_authors(field.value)
            case False:
                authors = field.value
            case x:
                raise TypeError(type(x))

        match authors:
            case str():
                result.append(authors)
            case [*xs] if self._do_name_parts:
                parts = [self._name_to_parts(x) for x in xs]
                result.append(model.Field(field.key, parts))
            case [*xs]:
                result.append(model.Field(field.key, list(xs)))
            case x:
                raise TypeError(type(x))

        return result

class NameMiddleware(BidiNames):

    def __init__(self, *args, authors:bool=True, parts:bool=True, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._reader = _NameReader(parts=parts, authors=authors)
        self._writer = NameWriter(parts=parts, authors=authors)
