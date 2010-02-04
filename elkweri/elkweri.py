#!/usr/bin/env python

"""
htmltester.py  (c) Antti Kaihola 2010

These tools provide a domain specific language for writing tests for
HTML/XHTML data.
"""

# The lxml library is used for parsing the markup and executing XPath
# queries.

from xpath_wrapper import Ekskweri
from step import Step

class Elkweri(Ekskweri, Step):
    pass
