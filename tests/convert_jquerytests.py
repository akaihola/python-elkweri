#!/usr/bin/env python

import re
import sys
from os.path import join, dirname

js = file(sys.argv[1]).read()

def sub(pattern, replacement):
    global js
    new_js = re.sub(pattern, replacement, js)
    if new_js == js:
        raise Warning('No match for %r' % pattern)
    js = new_js

def replace(pattern, replacement):
    global js
    new_js = js.replace(pattern, replacement)
    if new_js == js:
        raise Warning('No match for %r' % pattern)
    js = new_js

# test() calls become functions
sub(r'test\("(.*)\", function\(\) \{',
        lambda m: r'def test_%s():' % m.group(1)
        .replace(' ', '_')
        .replace('-', 'minus')
        .replace(':', 'colon_'))

# remove function endings
sub(r'\n\t*}(?:\);)?(?=\n)', '')

# no "var" keyword
sub(r'\bvar +', '')

# "all" is a reserved word
sub(r'\ball\b', 'all_nodes')

# comment symbol
sub(r'(?<=[\t ;])//', '##')

# opening brace to colon
sub(r'\{\n', ':\n')

# open and test with another data file
sub(r'jQuery.get\((".*"), function\(xml\)',
        r'with Djeikweri(join(dirname(__file__), \1)) as xml')

# definition of function "broken"
replace('function broken(name, selector)',
        'def broken(name, selector, _=None)')

# catch -> except
sub(r'}\s*catch\(e\)', 'except Exception, e')

# test if exception is a syntax error
replace('typeof e === "string" && e.indexOf("Syntax error") >= 0',
        'isinstance(e, SyntaxError)')

# typeof -> isinstance
#replace('typeof e === "string"', 'isinstance(e, str)')

# remove unnecessary and incorrectly indented if
# N.B. must be done before "|| -> or"
replace(
    '\nif ( (window.Sizzle || jQuery.find).selectors.filters.visibility ) :\n',
    '\n')

## && -> and  (only occurrence already replaced above)
#replace('&&', 'and')

## || -> or  (only occurrence already replaced above)
#replace('||', 'or')

# fix wrong indentation on line 137
replace('\n  ', '\n\t')

# invalid variable name
replace('$div', 'div_tags')

# a=1,b=2 -> a=1;b=2  and  true -> True
sub(', good = true', '; good = True')

# document.getElementsByTagName -> jQuery
#sub(r'document\.getElementsByTagName\((.*)\)',
#    r'jQuery(\1)')

# define encoding
replace('module("selector");', r'''
# -*- coding: utf-8 -*-

from os.path import join, dirname
from nose.tools import ok_, eq_
from elkweri.djeikweri import Djeikweri, Element
from djeikweri_basic_tests import same
import lxml.html

class location:
    protocol = None

def expect(n):
    global count
    count = n

def reset():
    pass

def start():
    pass

def stop():
    pass

def ok(test, name):
    if test:
        global count
        count -= 1
    ok_(test, name)

def equals(a, b, msg='Not equal'):
    eq_(a, b, '%s: %r\n\n!=\n\n%r' % (msg, a, b))

def t(name, query, id_list):
    equals(jQuery(query).get(), id_list)

class document:
    @staticmethod
    def getElementsByTagName(tagname):
        return jQuery(tagname)

    @staticmethod
    def createElement(tagname):
        return Element(tagname)

q = lambda *args: args

jQuery = Djeikweri(join(dirname(__file__), 'data/jquery_test.html'))
''')

def quote_string(match):
    s = match.group(1)
    if all(ord(c) < 128 for c in s):
        return '"%s"' % s
    return 'u"%s"' % s

# strings to Unicode objects
sub(r'(?<!\\)"([^"]*)"', quote_string)

file(join(dirname(__file__), 'djeikweri_tests.py'), 'w').write(js)
