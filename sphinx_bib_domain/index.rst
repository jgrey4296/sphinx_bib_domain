.. ..  index.rst -*- mode: ReST -*-

.. _index:

==========================
Sphinx Bibtex Domain
==========================

.. contents:: Table of Contents


------------
Introduction
------------

A `sphinx`_ `extension`_ for a `bibtex`_ domain.

Adds an ``entry`` `directive`_ , with accompanying `roles`_,
which are used to generate indices for ``author``'s ``institution``'s, ``journal``'s,
``publisher``'s, ``series``, and ``tag``'s.

For an example of this domain in use, see `my bibliography`_.

------------
Installation
------------

To install, run ``uv add --prerelease=allowed sphinx_bib_domain`` and sync
(prerelease is needed for the dependency on ```bibtexparser``).
Then, in your ``conf.py``:

.. code:: python
 
   extensions =  ["sphinx_bib_domain"]
          
   # To enable .bib file parsing:
   source_suffix = {".bib": "bibtex"}
   # To enable split domain-specific indices:
   bib_domain_split_index = True


--------------------------
Split Domain Index Builder
--------------------------

By calling ``sphinx-build --builder bibhtml``,
the :class:`~sphinx_bib_domain.builder.bib_html_builder.BibDomainHTMLBuilder`
will be called to run the build.
With ``bib_domain_split_index = True`` in the `conf.py` file, all domain-specific indices (eg: this bib domain)
will be built in a similar way to the standard split index of sphinx. 

--------------------------
The Bibtex Entry Directive
--------------------------

This is the main piece of this package.

.. code:: rst

   .. bibtex:entry:: a_key
      :title: An Example Entry
      :author: Bob
      :year: 2025
      :tags: example,bibtex
      :url: https://somewhere.com
            
         
This will be handled by the :class:`~sphinx_bib_domain.directives.bib_entry.BibEntryDirective`,
producing a description of the entry in a similar format to how sphinx
documents python code.


------------
BibtexParser
------------

The :class:`~sphinx_bib_domain.parser.BibtexParser` uses `bibble`_ to
parse bibtex and rewrite it to rst, which is then parsed to produce output.


.. _repo:

---------------
Repo And Issues
---------------

The repo can be found `here <https://github.com/jgrey4296/sphinx_bib_domain>`_.

If you find a bug, bug me, unsurprisingly, on the `issue tracker <https://github.com/jgrey4296/sphinx_bib_domain/issues>`_.


.. .. Main Sidebar TocTree
.. toctree::
   :maxdepth: 3
   :glob:
   :hidden:
      
   [a-z]*/index

   _docs/*
   genindex
   modindex
   API Reference <_docs/_autoapi/sphinx_bib_domain/index>
   

.. .. Links

.. _sphinx: https://www.sphinx-doc.org/en/master/

.. _bibtex: https://www.bibtex.com

.. _extension: https://www.sphinx-doc.org/en/master/development/index.html

.. _directive: https://www.sphinx-doc.org/en/master/glossary.html#term-directive

.. _roles: https://www.sphinx-doc.org/en/master/glossary.html#term-role

.. _my bibliography: https://jgrey4296.github.io/bibliography/

.. _bibble: https://bibble.readthedocs.io/en/latest/
