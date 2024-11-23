#!/usr/bin/env python2
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
from collections import defaultdict
from sys import stderr
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generator,
                    Generic, Iterable, Iterator, Mapping, Match,
                    MutableMapping, Protocol, Sequence, Tuple, TypeAlias,
                    TypeGuard, TypeVar, cast, final, overload,
                    runtime_checkable)
from urllib.parse import urlparse
from uuid import UUID, uuid1

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
from .directives import BibEntryDirective
from .roles import *

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging


def log(s, *args):
    print(s.format(*args), file=stderr)

def fsig(sig) -> str:
    return f"{DOMAIN_NAME}.{sig}"

def anchor(sig) -> str:
    return f"{DOMAIN_NAME}-{sig}"

class BibTexDomain(Domain):
    """ Custom Domain for sphixn
    register with app.add_domain(StandardDomain)
    """

    name         : str                                = DOMAIN_NAME
    label        : str                                = DOMAIN_NAME
    # directives, roles, indices to be registered rather than in setup:
    directives   : dict[str,type[Directive]]          = {'entry'        : BibEntryDirective}
    roles        : dict[str, Role]                    = {'ref'          : XRefRole(),
                                                         'tag'          : TagRole(),
                                                         'doi'          : DOIRole(),
                                                         "author"       : AuthorRole(),
                                                         "journal"      : JournalRole(),
                                                         "publisher"    : PublisherRole(),
                                                         "series"       : SeriesRole(),
                                                         "institution"  : InstitutionRole(),
                                                         }
    indices      : set[type[Index]]                   = {TagIndex, AuthorIndex, PublisherIndex, JournalIndex, InstitutionIndex, SeriesIndex}
    data_version                                      = 0
    # initial data to copy to env.domaindata[domain_name]
    initial_data                                   = {
        'entries'       : {},
        'tags'          : defaultdict(list),
        'authors'       : defaultdict(list),
        'publishers'    : defaultdict(list),
        'journals'      : defaultdict(list),
        'institutions'  : defaultdict(list),
        'series'        : defaultdict(list),
    }
    _static_virtual_names = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._virtual_names = {x.shortname : (f"{self.name}-{x.name}", x.localname) for x in self.indices}
        self._virtual_names.update(self._static_virtual_names)
        StandardDomain._virtual_doc_names.update(self._virtual_names)
        self._last_signature : None|str = None

    def get_full_qualified_name(self, node) -> str:
        return fsig(node.arguments[0])

    def get_objects(self) -> iterator[tuple[str, str, str, str, str, int]]:
        yield from self.data['entries'].values()

    def resolve_xref(self, env:BuildEnvironment, fromdocname:str, builder:Builder, typ:str, target:str, node:pending_xref, contnode:Element):
        """
        typ: cross ref type,
        target: target name
        """
        match typ:
            case "tag" if target in self.data['tags']:
                todocname = self._virtual_names["tagindex"][0]
                targ      = "cap-{}".format(target[0].upper())
                return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
            case "author" if target in self.data['authors']:
                todocname = self._virtual_names["authorindex"][0]
                targ      = "cap-{}".format(target[0].upper())
                return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
            case "publisher" if target in self.data['publishers']:
                todocname = self._virtual_names["pubindex"][0]
                targ      = "cap-{}".format(target[0].upper())
                return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
            case "journal" if target in self.data['journals']:
                todocname = self._virtual_names["jourindex"][0]
                targ      = "cap-{}".format(target[0].upper())
                return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
            case "institution" if target in self.data['institutions']:
                todocname = self._virtual_names["instindex"][0]
                targ      = "cap-{}".format(target[0].upper())
                return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
            case "series" if target in self.data['series']:
                todocname = self._virtual_names["seriesindex"][0]
                targ      = "cap-{}".format(target[0].upper())
                return make_refnode(builder, fromdocname, todocname, targ, contnode, targ)
            case _:
                log("Found other XRef Type: {} : ({})", typ, target)

    def add_entry(self, signature):
        """Add a new entry to the domain."""
        self._last_signature = fsig(signature)
        anchor_s             = anchor(signature)
        # name, dispname, type, docname, anchor, priority
        self.data['entries'][self._last_signature] = (self._last_signature, signature, self.env.docname,  anchor_s, '', 1)

    def link_tags(self, tags:list[str]):
        if not self._last_signature:
            return

        sig_s = self._last_signature
        for tag in tags:
            self.data['tags'][tag].append(sig_s)

    def link_authors(self, authors:list[str]):
        if not self._last_signature:
            return

        for author in authors:
            self.data['authors'][author].append(self._last_signature)

    def link_publisher(self, publisher:str):
        if not self._last_signature:
            return

        self.data['publishers'][publisher].append(self._last_signature)

    def link_journal(self, journal:str):
        if not self._last_signature:
            return

        self.data['journals'][journal].append(self._last_signature)

    def link_institution(self, institution:str):
        if not self._last_signature:
            return

        self.data['institutions'][institution].append(self._last_signature)

    def link_series(self, series:str):
        if not self._last_signature:
            return

        self.data['series'][series].append(self._last_signature)
