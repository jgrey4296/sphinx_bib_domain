#!/usr/bin/env python3
"""

"""
# mypy: disable-error-code="import-untyped, import-not-found"
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
from uuid import UUID, uuid1
from urllib.parse import urlparse

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

from .. import _interface as API

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload

if TYPE_CHECKING:
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from sphinx.util.typing import ExtensionMetadata, OptionSpec
    type desc_signature = addnodes.desc_signature
    type Node = nodes.Node
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging


class BibEntryDirective(ObjectDescription):
    """ Custom Directive for Bibtex Entries.
    Note: use 'within' for volume, number, issue, pages.
    concat title with subtitle

    TODO: legal fields (status, plaintiff, defendant etc)
    """

    has_content        : bool = True
    required_arguments : int = 1
    option_spec        : ClassVar[OptionSpec] = {
        'title'       : directives.unchanged_required,
        'year'        : directives.unchanged_required,
        'tags'        : directives.unchanged_required,
        'author'      : directives.unchanged,
        'editor'      : directives.unchanged,
        'journal'     : directives.unchanged,
        'booktitle'   : directives.unchanged,
        'within'      : directives.unchanged,
        'platform'    : directives.unchanged,
        'publisher'   : directives.unchanged,
        'institution' : directives.unchanged,
        'series'      : directives.unchanged,
        'url'         : directives.unchanged,
        'doi'         : directives.unchanged,
        'isbn'        : directives.unchanged,
        'edition'     : directives.unchanged,
        'crossref'    : directives.unchanged,
        # TODO : thesis type
    }

    def before_content(self):
        """ Set the content to be rendered from the options passed in """
        adapted                        = []
        title, authors, tags, crossref = "", "", "", ""
        loc, loc_details               = "", ""
        url, doi                       = "", ""

        for x,y in self.options.items():
            match x:
                case "title":
                    title = f"| *{y}*"
                case "author" | "editor":
                    _authors = " and ".join(f":author:`{a.strip()}`" for a in y.split(" and "))
                    eds = " (eds)." if x == "editor" else ""
                    authors  = f"| {_authors}{eds}"
                case "tags":
                    tags    = ", ".join(f":tag:`{t.strip()}`" for t in y.split(","))
                case "crossref":
                    crossref = f"| :ref:`{y}`__"
                case "edition":
                    adapted.append(f"| {y} Edition")
                case "url":
                    url_ = urlparse(y)
                    url = f"| `link <{y}>`__"
                case "doi":
                    doi = f"| :doi:`{y}`"
                case "within":
                    adapted.append(f"| in *{y}*")
                case "journal":
                    adapted.append(f"| in :journal:`{y}`")
                case "series":
                    adapted.append(f"| :series:`{y}`")
                case "institution":
                    adapted.append(f"| :institution:`{y}`")
                case "publisher":
                    adapted.append(f"| :publisher:`{y}`")
                case "year" | "platform":
                    pass
                case "isbn":
                    adapted.append(f"| isbn: {y}")
                case "booktitle":
                    adapted.append(f"| in *{y}*")
                case _:
                    adapted.append(f"| {y}")

        # Ensure title and authors are first
        adapted = [title, authors, *adapted]
        # and tags + crossref are last
        if doi:
            adapted.append(doi)
        if url:
            adapted.append(url)
        if crossref:
            adapted.append(f"See :ref:`{self.options['crossref']}`")
        if tags:
            adapted.append(f"| {tags}")

        self.content = "\n".join(adapted)

    def _toc_entry_name(self, sig_node:desc_signature) -> str:
        return ''

    def handle_signature(self, sig:str, signode:addnodes.desc_signature) -> Node:
        """ parses the signature and passes the name and type on """
        signode += addnodes.desc_name(text=sig)
        return sig

    def add_target_and_index(self, name_cls, sig, signode):
        """ links the node to the index and back """
        signode['ids'].append(API.anchor(sig))
        self.state.document.note_explicit_target(signode)
        domain = self.env.get_domain(API.DOMAIN_NAME)
        domain.add_entry(sig)
        for x,y in self.options.items():
            match x:
                case "author" | "editor":
                    domain.link_authors([x.strip() for x in y.split(" and ")])
                case "tags":
                    domain.link_tags([x.strip() for x in self.options['tags'].split(",")])
                case "publisher":
                    domain.link_publisher(y)
                case "institution":
                    domain.link_institution(y)
                case "series":
                    domain.link_series(y)
                case "journal":
                    domain.link_journal(y)
                case _:
                    pass
