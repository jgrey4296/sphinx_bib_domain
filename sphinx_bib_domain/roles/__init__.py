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

# ##-- end stdlib imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# ##-- 3rd party imports
from sphinx.roles import AnyXRefRole, ReferenceRole, XRefRole
from docutils import nodes
# ##-- end 3rd party imports

# ##-- 1st party imports
from sphinx_bib_domain import DOMAIN_NAME

# ##-- end 1st party imports

Node           = "node"
system_message = "System_Message"

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
