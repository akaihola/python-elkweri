===================================
 Elkweri -- a DSL for testing HTML
===================================

At this point the only documentation is the following suite of examples.

Prepare a HTML page for testing by parsing it::

    >>> from elkweri import Elkweri
    >>> page = Elkweri(u'<html><body><div id="main">'
    ...                u'<p class="para" id="para1">This</p>'
    ...                u'<p class="para" id="para2">is '
    ...                u'<span class="inner"><a href="link">a</a></span></p>'
    ...                u'<p class="lastpara" id="para3">a '
    ...                u'<span class="inner">test</span></p>'
    ...                u'</div></body></html>')

The ``page`` object represents the root ``<html>`` tag of the DOM
tree.  The number of elements returned by a query can be retrieved
using the standard Python ``len()`` function::

    >>> len(page)
    1

The ``.tag`` property returns a the tags of the queried elements as a
list::

    >>> page.tag
    ['html']

The ``elkweri.tags`` module defines HTML tag matchers for your
convenience.  The ``p`` object matches ``<P>`` tags.  Any tag can be
matched with the ``x`` object, which corresponds to ``*`` in XPath and
jQuery::
 
    >>> from elkweri.tags import p, x, div, span

The ``//`` operator selects descendants of an element. It corresponds
to ``//`` in XPath and a space in jQuery selectors::

    >>> (page // x).tag
    ['html', 'body', 'div', 'p', 'p', 'span', 'a', 'p', 'span']

The ``/`` operator selects immediate children of an element. It
corresponds to ``/`` in XPath and ``>`` in jQuery::

    >>> (page // div / x).tag
    ['p', 'p', 'p']

Values of element attributes are accessed with string subscripts::

    >>> (page // p)['id']
    ['para1', 'para2', 'para3']

Elements with given ``id`` attributes can be matched with a string
argument prefixed with ``"#"``::

    >>> (page // x('#main')).tag
    ['div']

To assert that an ``id`` exists in a document::

    >>> assert page // x('#main')
    >>> assert page // x('#nonexistent')
    Traceback (most recent call last):
    AssertionError

Similarly, tags containing a given class are matched with a string
argument prefixed with a period::

    >>> (page // x('.para')).tag
    ['p', 'p']
    >>> assert page // x('.para')

To assert that an element with both the given ``id`` and class
exists::

    >>> assert page // x('#para3', '.lastpara')
    >>> assert page // x('#para4', '.lastpara')
    Traceback (most recent call last):
    AssertionError

The text content of an element can be matched with
``.text_equals()``::

    >>> assert page // span('.inner').text_equals('x')
    Traceback (most recent call last):
    AssertionError
    >>> assert page // span('.inner').text_equals('test')

The ``^`` operator corresponds to ``following-sibling`` in XPath and
``~`` in jQuery::

    >>> (page // p ^ p)['id']
    ['para2', 'para3']
    >>> assert page // p ^ p('#para2')
    >>> assert page // p ^ p('#para1')
    Traceback (most recent call last):
    AssertionError

The ``+`` operator matches the next sibling::

    >>> (page // x('#para1') + p)['id']
    ['para2']

Finally, the ``<`` operator matches elements which have the following
elements as children.  Here only ``<P>`` tags containing ``<SPAN>``
elements are matched::

    >>> print (page // p < span).tag
    ['p', 'p']

    >>> from elkweri.tags import a

    >>> assert (page // p < (span / a)).tag == ['p']

    >>> [el.tag for el in (page // p < (span / a)).union(page // p)]
    ['p', 'p', 'p']

Example: testing forms
======================

    >>> from elkweri.tags import html, body, form, input

    >>> form1 = Elkweri(
    ...     u'<form method="post" action=".">'
    ...     u'<input type="text" name="last_name" id="id_last_name" value="Ek" />'
    ...     u'<input type="submit" value="Send" />'
    ...     u'</form>') / html / body / form

    >>> assert form1
    >>> assert form1.tag == ['form']
    >>> assert form1 / input
    >>> assert len(form1 / input) == 2
    >>> assert form1 / input(name='last_name', id='id_last_name', value='Ek')
    >>> assert not form1 / input(name='last_name', id='id_last_name', value='Ahl')
    >>> assert form1 / input(type='submit', value='Send')
    >>> assert (form1 / input).tag, ['input' == 'input']
    >>> assert (form1 / input)[0]('#id_last_name')
    >>> assert (form1 / input('#id_last_name'))[0]
    >>> assert not (form1 / input)[0]('#id_first_name')
    >>> assert not (form1 / input('#id_first_name'))[0]
