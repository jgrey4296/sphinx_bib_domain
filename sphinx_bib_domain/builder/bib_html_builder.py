#!/usr/bin/env python3
"""


"""
# ruff: noqa:

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
import collections
import contextlib
import hashlib
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
import atexit # for @atexit.register
import faulthandler
# ##-- end stdlib imports

import jinja2.exceptions
import contextlib
import os
import html
from sphinx.util.osutil impoprt relative_uri
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.builders.html._assets import _JavaScript, _CascadingStyleSheet, _file_checksum
from sphinx.errors import ConfigError, ThemeError

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType, Never
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload
# from dataclasses import InitVar, dataclass, field
# from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError

if TYPE_CHECKING:
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

class BibDomainHTMLBuilder(StandaloneHTMLBuilder):
    """ Customised Sphinx HTML builder

    Primarily for enabling split domain indices.

    """

    def write_domain_indices(self) -> None:
        for index_name, index_cls, content, collapse in self.domain_indices:
            index_context = {
                'indextitle': index_cls.localname,
                'content': content,
                'collapse_index': collapse,
            }
            logger.info('%s ', index_name, nonl=True)
            self.handle_split_domain_index_page(index_name, index_context, 'domainindex.html')



    def pathto(self, otheruri: str, resource: bool = False, baseuri: str = default_baseuri,) -> str:
        if resource and '://' in otheruri:
            # allow non-local resources given by scheme
            return otheruri
        elif not resource:
            otheruri = self.get_target_uri(otheruri)
        uri = relative_uri(baseuri, otheruri) or '#'
        if uri == '#' and not self.allow_sharp_as_current_path:
            uri = baseuri
        return uri


    def hasdoc(self, name: str) -> bool:
        if name in self.env.all_docs:
            return True
        if name == 'search' and self.search:
            return True
        return (name == 'genindex'
                and self.get_builder_config('use_index', 'html'))


    def js_tag(self, js: _JavaScript | str) -> str:
        if not isinstance(js, _JavaScript):
            # str value (old styled)
            return f'<script src="{self.pathto(js, resource=True)}"></script>'

        body = js.attributes.get('body', '')
        attrs = [
            f'{key}="{html.escape(value, quote=True)}"'
            for key, value in js.attributes.items()
            if key != 'body' and value is not None
        ]

        if not js.filename:
            if attrs:
                return f'<script {" ".join(sorted(attrs))}>{body}</script>'
            return f'<script>{body}</script>'

        js_filename_str = os.fspath(js.filename)
        uri = self.pathto(js_filename_str, resource=True)
        if 'MathJax.js?' in js_filename_str:
            # MathJax v2 reads a ``?config=...`` query parameter,
            # special case this and just skip adding the checksum.
            # https://docs.mathjax.org/en/v2.7-latest/configuration.html#considerations-for-using-combined-configuration-files
            # https://github.com/sphinx-doc/sphinx/issues/11658
            pass
        # the EPUB format does not allow the use of query components
        elif self.name != 'epub':
            if checksum := _file_checksum(outdir, js.filename):
                uri += f'?v={checksum}'
        if attrs:
            return f'<script {" ".join(sorted(attrs))} src="{uri}"></script>'
        return f'<script src="{uri}"></script>'

    def css_tag(self, css: _CascadingStyleSheet) -> str:
        attrs = [
            f'{key}="{html.escape(value, quote=True)}"'
            for key, value in css.attributes.items()
            if value is not None
        ]
        uri = self.pathto(os.fspath(css.filename), resource=True)
        # the EPUB format does not allow the use of query components
        # the Windows help compiler requires that css links
        # don't have a query component
        if self.name not in {'epub', 'htmlhelp'}:
            if checksum := _file_checksum(outdir, css.filename):
                uri += f'?v={checksum}'
        return f'<link {" ".join(sorted(attrs))} href="{uri}" />'



    def write_genindex(self) -> None:
        # the total count of lines for each index letter, used to distribute
        # the entries into two columns
        genindex = IndexEntries(self.env).create_index(self)
        indexcounts = [
            sum(1 + len(subitems) for _, (_, subitems, _) in entries)
            for _k, entries in genindex
        ]

        genindexcontext = {
            'genindexentries': genindex,
            'genindexcounts': indexcounts,
            'split_index': self.config.html_split_index,
        }
        logger.info('genindex ', nonl=True)

        if self.config.html_split_index:
            self.handle_page('genindex', genindexcontext, 'genindex-split.html')
            self.handle_page('genindex-all', genindexcontext, 'genindex.html')
            for (key, entries), count in zip(genindex, indexcounts, strict=True):
                ctx = {
                    'key': key,
                    'entries': entries,
                    'count': count,
                    'genindexentries': genindex,
                }
                self.handle_page('genindex-' + key, ctx, 'genindex-single.html')
        else:
            self.handle_page('genindex', genindexcontext, 'genindex.html')

    def handle_split_domain_index_page(self, pagename:str, addctx:dict[str, Any], templatename:str='page.html', *, outfilename:Path|None=None, event_arg:Any=None) -> None:
        """ A domain-specific split index creator

        write_genindex shows how sphinx does it.
        """
        ctx = self.globalcontext.copy()
        # current_page_name is backwards compatibility
        ctx['pagename'] = ctx['current_page_name'] = pagename
        ctx['encoding'] = self.config.html_output_encoding
        default_baseuri = self.get_target_uri(pagename)
        # in the singlehtml builder, default_baseuri still contains an #anchor
        # part, which relative_uri doesn't really like...
        default_baseuri = default_baseuri.rsplit('#', 1)[0]

        if self.config.html_baseurl:
            ctx['pageurl'] = posixpath.join(
                self.config.html_baseurl, self.get_target_uri(pagename)
            )
        else:
            ctx['pageurl'] = None

        ctx['pathto'] = self.pathto
        ctx['hasdoc'] = self.hasdoc

        ctx['toctree'] = lambda **kwargs: self._get_local_toctree(pagename, **kwargs)
        self.add_sidebars(pagename, ctx)
        ctx.update(addctx)

        # 'blah.html' should have content_root = './' not ''.
        ctx['content_root'] = (f'..{SEP}' * default_baseuri.count(SEP)) or f'.{SEP}'

        outdir = self.app.outdir

        ctx['css_tag'] = self.css_tag
        ctx['js_tag'] = self.js_tag

        # revert _css_files and _js_files
        self._css_files[:] = self._orig_css_files
        self._js_files[:] = self._orig_js_files

        self.update_page_context(pagename, templatename, ctx, event_arg)
        if new_template := self.events.emit_firstresult(
            'html-page-context', pagename, templatename, ctx, event_arg
        ):
            templatename = new_template

        # sort JS/CSS before rendering HTML
        try:  # NoQA: SIM105
            # Convert script_files to list to support non-list script_files
            # See: https://github.com/sphinx-doc/sphinx/issues/8889
            ctx['script_files'] = sorted(
                ctx['script_files'], key=lambda js: js.priority
            )
        except AttributeError:
            # Skip sorting if users modifies script_files directly (maybe via `html_context`).
            # See: https://github.com/sphinx-doc/sphinx/issues/8885
            #
            # Note: priority sorting feature will not work in this case.
            pass

        with contextlib.suppress(AttributeError):
            ctx['css_files'] = sorted(ctx['css_files'], key=lambda css: css.priority)

        try:
            output = self.templates.render(templatename, ctx)
        except UnicodeError:
            logger.warning(
                __(
                    'a Unicode error occurred when rendering the page %s. '
                    'Please make sure all config values that contain '
                    'non-ASCII content are Unicode strings.'
                ),
                pagename,
            )
            return
        except Exception as exc:
            if (
                isinstance(exc, jinja2.exceptions.UndefinedError)
                and exc.message == "'style' is undefined"
            ):
                msg = __(
                    "The '%s' theme does not support this version of Sphinx, "
                    "because it uses the 'style' field in HTML templates, "
                    'which was  was deprecated in Sphinx 5.1 and removed in Sphinx 7.0. '
                    "The theme must be updated to use the 'styles' field instead. "
                    'See https://www.sphinx-doc.org/en/master/development/html_themes/templating.html#styles'
                )
                raise ThemeError(msg % self.config.html_theme) from None

            msg = __('An error happened in rendering the page %s.\nReason: %r') % (
                pagename,
                exc,
            )
            raise ThemeError(msg) from exc

        if outfilename:
            output_path = Path(outfilename)
        else:
            output_path = self.get_output_path(pagename)
        # The output path is in general different from self.outdir
        ensuredir(output_path.parent)
        try:
            output_path.write_text(
                output, encoding=ctx['encoding'], errors='xmlcharrefreplace'
            )
        except OSError as err:
            logger.warning(__('error writing file %s: %s'), output_path, err)
        if self.copysource and ctx.get('sourcename'):
            # copy the source file for the "show source" link
            source_file_path = self._sources_dir / ctx['sourcename']
            source_file_path.parent.mkdir(parents=True, exist_ok=True)
            copyfile(self.env.doc2path(pagename), source_file_path, force=True)
