#!/usr/bin/env python3

__version__ = "0.0.1"


def setup(app):
    from .bib_domain import BibTexDomain
    app.add_domain(BibTexDomain)
