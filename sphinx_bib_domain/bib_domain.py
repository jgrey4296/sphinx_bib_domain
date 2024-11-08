#!/usr/bin/env python2
"""

See EOF for license/metadata/notes as applicable
"""

from __future__ import annotations

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
from urllib.parse import urlparse
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generator,
                    Generic, Iterable, Iterator, Mapping, Match,
                    MutableMapping, Protocol, Sequence, Tuple, TypeAlias,
                    TypeGuard, TypeVar, cast, final, overload,
                    runtime_checkable)
from uuid import UUID, uuid1

from sys import stderr
from collections import defaultdict
from docutils.parsers.rst import directives
from docutils import nodes
from sphinx.domains import Index, IndexEntry
from sphinx.roles import AnyXRefRole, XRefRole, ReferenceRole
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.domains import Domain, ObjType
from sphinx.domains.std import StandardDomain

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

DOMAIN_NAME : Final[str] = "bibtex"
# TODO Proceeding index

def log(s, *args):
    print(s.format(*args), file=stderr)

def setup(app):
    app.add_domain(BibTexDomain)

def fsig(sig) -> str:
    return f"{DOMAIN_NAME}.{sig}"

def anchor(sig) -> str:
    return f"{DOMAIN_NAME}-{sig}"

class TagRole(XRefRole):
    """ A Role for marking tags and linking to the tag index """
    lowercase = True
    classes   = ['xref', 'tag']
    refdomain = DOMAIN_NAME
    reftype   = "tag"

    def run(self) -> tuple[list[Node], list[system_message]]:
        # log("Tagging: {} in {}", self.title, self.env.docname)
        nodes, msgs = self.create_xref_node()
        return nodes, msgs

class AuthorRole(XRefRole):
    """ A Role for marking authors and linking to the index """
    lowercase = True

    classes   = ['author']
    refdomain = DOMAIN_NAME
    reftype   = "author"

    def run(self) -> tuple[list[Node], list[system_message]]:
        # log("Tagging: {} in {}", self.title, self.env.docname)
        nodes, msgs = self.create_xref_node()
        return nodes, msgs

class PublisherRole(XRefRole):
    """ A Role for marking publishers and linking to the index """
    lowercase = True

    classes   = ['publisher']
    refdomain = DOMAIN_NAME
    reftype   = "publisher"

    def run(self) -> tuple[list[Node], list[system_message]]:
        # log("Tagging: {} in {}", self.title, self.env.docname)
        nodes, msgs = self.create_xref_node()
        return nodes, msgs

class JournalRole(XRefRole):
    """ A Role for marking journals and linking to the index """
    lowercase = True

    classes   = ['journal']
    refdomain = DOMAIN_NAME
    reftype   = "journal"

    def run(self) -> tuple[list[Node], list[system_message]]:
        # log("Tagging: {} in {}", self.title, self.env.docname)
        nodes, msgs = self.create_xref_node()
        return nodes, msgs

class InstitutionRole(XRefRole):
    """ A Role for marking institutions and linking to the index """
    lowercase = True

    classes   = ['institution']
    refdomain = DOMAIN_NAME
    reftype   = "institution"

    def run(self) -> tuple[list[Node], list[system_message]]:
        # log("Tagging: {} in {}", self.title, self.env.docname)
        nodes, msgs = self.create_xref_node()
        return nodes, msgs

class SeriesRole(XRefRole):
    """ A Role for marking seriess and linking to the index """
    lowercase = True

    classes   = ['series']
    refdomain = DOMAIN_NAME
    reftype   = "series"

    def run(self) -> tuple[list[Node], list[system_message]]:
        # log("Tagging: {} in {}", self.title, self.env.docname)
        nodes, msgs = self.create_xref_node()
        return nodes, msgs

class DOIRole(XRefRole):
    """ A Role for linking to doi's"""

    classes   = ['xref', 'doi']
    refdomain = DOMAIN_NAME
    reftype   = "doi"

    def run(self) -> tuple[list[Node], list[system_message]]:
        # log("Doi: {} in {}", self.title, self.env.docname)
        uri = f"https://doi.org/{self.title}"
        ref = nodes.reference('', '', internal=False, refuri=uri, classes=self.classes)
        ref += nodes.literal("DOI", "DOI")

        return [ref], []

class BibEntryDirective(ObjectDescription):
    """ Custom Directive for Bibtex Entries.
    Note: use 'within' for volume, number, issue, pages.
    concat title with subtitle

    TODO: legal fields (status, plaintiff, defendant etc)
    """

    has_content        = True
    required_arguments = 1
    option_spec        = {
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
        adapted = [title, authors] + adapted
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

    def handle_signature(self, sig:str, signode:addnoes.desc_signature) -> Node:
        """ parses the signature and passes the name and type on """
        signode += addnodes.desc_name(text=sig)
        return sig

    def add_target_and_index(self, name_cls, sig, signode):
        """ links the node to the index and back """
        signode['ids'].append(anchor(sig))
        self.state.document.note_explicit_target(signode)
        domain = self.env.get_domain(DOMAIN_NAME)
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

class TagIndex(Index):
    """ A Custom index for sphinx """

    name      = 'tag-index'
    localname = 'Tag Index'
    shortname = 'tagindex'

    def generate(self, docnames=None) -> tuple[list, bool]:
        content : dict[str, list[IndexEntry]] = defaultdict(list)
        collapse = True
        entries = self.domain.data['entries']

        for tag, sigs in self.domain.data['tags'].items():
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

        for author, sigs in self.domain.data['authors'].items():
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

        for pub, sigs in self.domain.data['publishers'].items():
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

        for journal, sigs in self.domain.data['journals'].items():
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

        for institution, sigs in self.domain.data['institutions'].items():
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

        for series, sigs in self.domain.data['series'].items():
            letter = series[0].upper()
            content[letter].append(IndexEntry(series, 1, "",  "", "", "", ""))
            for sig in sigs:
                if sig not in entries:
                    continue
                obj = entries[sig]
                name = obj[0].removeprefix(f"{DOMAIN_NAME}.")
                content[letter].append(IndexEntry(name, 2, obj[2], obj[3], '', '', ''))

        return sorted(content.items()), collapse

class BibTexDomain(Domain):
    """ Custom Domain for sphixn
    register with app.add_domain(StandardDomain)
    """

    name         : str                                = DOMAIN_NAME
    label        : str                                = DOMAIN_NAME
    # directives, roles, indices to be registered rather than in setup:
    directives   : dict[str,type[Directive]]          = {'entry': BibEntryDirective}
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
