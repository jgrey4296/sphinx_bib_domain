#!/usr/bin/env python3

from importlib import metadata

__version__ = metadata.version("sphinx_bib_domain")

def setup(app):
    from .bib_domain import BibTexDomain
    from .builder import BibDomainHTMLBuilder
    app.add_domain(BibTexDomain)
    app.add_builder(BibDomainHTMLBuilder)

    # app.add_config_value
