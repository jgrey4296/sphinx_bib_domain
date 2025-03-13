#!/usr/bin/env python3

__version__ = "0.0.1"

from .bib_domain import BibTexDomain

def setup(app):
    app.add_domain(BibTexDomain)
