#!/usr/bin/env python3
"""

"""

# Imports:
from __future__ import annotations

# ##-- stdlib imports
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import types
import weakref
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generator,
                    Generic, Iterable, Iterator, Mapping, Match,
                    MutableMapping, Protocol, Sequence, Tuple, TypeAlias,
                    TypeGuard, TypeVar, cast, final, overload,
                    runtime_checkable)
from uuid import UUID, uuid1
from collections import defaultdict

# ##-- end stdlib imports

# ##-- 3rd party imports
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, Index, IndexEntry, ObjType
from sphinx.domains.std import StandardDomain
from sphinx.roles import AnyXRefRole, ReferenceRole, XRefRole
from sphinx.util.nodes import make_refnode

# ##-- end 3rd party imports

from sphinx_bib_domain import DOMAIN_NAME

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# TODO Proceeding index

class TagIndex(Index):
    """ A Custom index for sphinx """

    name      = 'tag-index'
    localname = 'Tag Index'
    shortname = 'tagindex'

    def generate(self, docnames=None) -> tuple[list, bool]:
        content : dict[str, list[IndexEntry]] = defaultdict(list)
        collapse = True
        entries = self.domain.data['entries']

        for tag in sorted(self.domain.data['tags'].keys()):
            sigs = sorted(self.domain.data['tags'][tag])
            if not bool(sigs):
                continue
            letter = tag[0].upper()
            content[letter].append(IndexEntry(tag, 1, "",  "", "", "", ""))
            for sig in sigs:
                if sig not in entries:
                    continue
                obj = entries[sig]
                name = obj[0].removeprefix(f"{DOMAIN_NAME}.")
                content[letter].append(IndexEntry(name, 2, obj[2], obj[3], '', '', ''))

        return sorted(content.items()), collapse

class AuthorIndex(Index):
    """ A Custom index for sphinx """

    name      = 'author-index'
    localname = 'Author/Editor Index'
    shortname = 'authorindex'

    def generate(self, docnames=None) -> tuple[Any, bool]:
        """ """
        content : dict[str, list[IndexEntry]] = defaultdict(list)
        collapse = True
        entries = self.domain.data['entries']

        for author, sigs in sorted(self.domain.data['authors'].items()):
            sigs = sorted(sigs)
            letter = author[0].upper()
            content[letter].append(IndexEntry(author, 1, "",  "", "", "", ""))
            for sig in sigs:
                if sig not in entries:
                    continue
                obj = entries[sig]
                name = obj[0].removeprefix(f"{DOMAIN_NAME}.")
                content[letter].append(IndexEntry(name, 2, obj[2], obj[3], '', '', ''))

        return sorted(content.items()), collapse

class PublisherIndex(Index):
    """ A Custom index for sphinx """

    name      = 'publisher-index'
    localname = 'Publisher Index'
    shortname = 'pubindex'

    def generate(self, docnames=None) -> tuple[Any, bool]:
        """ """
        content : dict[str, list[IndexEntry]] = defaultdict(list)
        collapse = True
        entries = self.domain.data['entries']

        for pub, sigs in sorted(self.domain.data['publishers'].items()):
            sigs = sorted(sigs)
            letter = pub[0].upper()
            content[letter].append(IndexEntry(pub, 1, "",  "", "", "", ""))
            for sig in sigs:
                if sig not in entries:
                    continue
                obj = entries[sig]
                name = obj[0].removeprefix(f"{DOMAIN_NAME}.")
                content[letter].append(IndexEntry(name, 2, obj[2], obj[3], '', '', ''))

        return sorted(content.items()), collapse

class JournalIndex(Index):
    """ A Custom index for sphinx """

    name      = 'journal-index'
    localname = 'Journal Index'
    shortname = 'jourindex'

    def generate(self, docnames=None) -> tuple[Any, bool]:
        """ """
        content : dict[str, list[IndexEntry]] = defaultdict(list)
        collapse = True
        entries = self.domain.data['entries']

        for journal, sigs in sorted(self.domain.data['journals'].items()):
            sigs = sorted(sigs)
            letter = journal[0].upper()
            content[letter].append(IndexEntry(journal, 1, "",  "", "", "", ""))
            for sig in sigs:
                if sig not in entries:
                    continue
                obj = entries[sig]
                name = obj[0].removeprefix(f"{DOMAIN_NAME}.")
                content[letter].append(IndexEntry(name, 2, obj[2], obj[3], '', '', ''))

        return sorted(content.items()), collapse

class InstitutionIndex(Index):
    """ A Custom index for sphinx """

    name      = 'institution-index'
    localname = 'Institution Index'
    shortname = 'instindex'

    def generate(self, docnames=None) -> tuple[Any, bool]:
        """ """
        content : dict[str, list[IndexEntry]] = defaultdict(list)
        collapse = True
        entries = self.domain.data['entries']

        for institution, sigs in sorted(self.domain.data['institutions'].items()):
            sigs = sorted(sigs)
            letter = institution[0].upper()
            content[letter].append(IndexEntry(institution, 1, "",  "", "", "", ""))
            for sig in sigs:
                if sig not in entries:
                    continue
                obj = entries[sig]
                name = obj[0].removeprefix(f"{DOMAIN_NAME}.")
                content[letter].append(IndexEntry(name, 2, obj[2], obj[3], '', '', ''))

        return sorted(content.items()), collapse

class SeriesIndex(Index):
    """ A Custom index for sphinx """

    name      = 'series-index'
    localname = 'Series Index'
    shortname = 'seriesindex'

    def generate(self, docnames=None) -> tuple[Any, bool]:
        """ """
        content : dict[str, list[IndexEntry]] = defaultdict(list)
        collapse = True
        entries = self.domain.data['entries']

        for series, sigs in sorted(self.domain.data['series'].items()):
            sigs = sorted(sigs)
            letter = series[0].upper()
            content[letter].append(IndexEntry(series, 1, "",  "", "", "", ""))
            for sig in sigs:
                if sig not in entries:
                    continue
                obj = entries[sig]
                name = obj[0].removeprefix(f"{DOMAIN_NAME}.")
                content[letter].append(IndexEntry(name, 2, obj[2], obj[3], '', '', ''))

        return sorted(content.items()), collapse
