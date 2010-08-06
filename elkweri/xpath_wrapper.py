import lxml.html
from lxml.etree import tostring, XPathEvalError, XPathEvaluator, ParserError

def simple_attrs(attrs):
    return sorted((attname, value) for attname, value in attrs.items()
                  if '__' not in attname)

def complex_attrs(attrs):
    return sorted(attname.split('__') + [value]
                  for attname, value in attrs.items()
                  if '__' in attname)

def make_filters(attrs):
    """Convert a dict of HTML tag attributes to XPath filters

    For unit testing purposes, we'll always output XPath filters in a
    predictable order.  This generator first yields the 'id' and
    'class' items from a dictionary, then the rest of the items sorted
    alphabetically.
    """
    simple = ['[@%s="%s"]' % (attname, value)
              for attname, value in simple_attrs(attrs)]
    complx = ['[%s(@%s, "%s")]' % (fn, attname, value)
              for attname, fn, value in complex_attrs(attrs)]
    return ''.join(simple + complx)

def has_word(evaluator, s, word):
    return s and word in s[0].split()

extensions = [{(None, 'has_word'): has_word}]

class XPathStep(object):
    "The Step class represents one step in an XPath expression"

    def __init__(self, xpath, is_union=False):
        self.xpath = xpath
        self.is_union = is_union

    def _filter(self, tail, other=None, prefix='', is_union=False):
        if isinstance(other, XPathStep) and other.is_union:
            raise SyntaxError("Can't embed union XPath expressions")
        if other is None:
            real_tail = tail
        elif isinstance(other, basestring):
            real_tail = tail % other
        else:
            real_tail = tail % other.xpath
        return self._clone('%s%s%s' % (prefix, self.xpath, real_tail), is_union)

    def _clone(self, xpath, is_union):
        return self.__class__(xpath, is_union)

    @classmethod
    def reverse(cls, meth):
        def rmeth(self, other):
            from elkweri import Elkweri
            return meth(Elkweri(other), self)
        return rmeth

    def descendant(self, other):
        "XPath //"
        return self._filter('//%s', other)

    def child(self, other):
        "XPath /"
        return self._filter('/%s', other)

    def has_child(self, other):
        "XPath [expr]"
        return self._filter('[%s]', other)

    def next(self, other):
        "jQuery +, XPath first following-sibling"
        return self._filter('/following-sibling::%s[1]', other)

    def following(self, other):
        "jQuery ~, XPath following-sibling"
        return self._filter('/following-sibling::%s', other)

    def eq(self, index):
        "jQuery :eq(index), XPath [index]"
        return self._filter(')[%d]' % (index + 1), prefix='(')

    def position(self, index):
        "XPath [position()=index]"
        return self._filter('[%d]' % (index + 1))

    def getattr(self, attname):
        "jQuery [attribute], XPath /@attribute"
        return self._filter('/@%s' % attname)

    def union(self, other):
        "jQuery ',', XPath |"
        return self._filter('|%s)', other,
                            prefix='(',
                            is_union=True)

    def attr(self, attrs):
        return self._filter(make_filters(attrs))

    def has_class(self, klass):
        return self._filter('[has_word(@class, "%s")]', klass)

    def text_equals(self, text):
        return self._filter('[text()="%s"]' % text)

class Ekskweri(XPathStep):
    """A DOM tree with query methods"""
    def __init__(self, document, xpath='', *args, **kwargs):
        super(Ekskweri, self).__init__(xpath, *args, **kwargs)
        try:
            document = file(document).read()
        except (TypeError, IOError):
            pass
        try:
            assert callable(document.element.xpath)
            self.dom = document.element
        except (AttributeError, AssertionError):
            try:
                assert callable(document.xpath)
                self.dom = document
            except (AttributeError, AssertionError):
                try:
                    self.dom = lxml.html.fragment_fromstring(document)
                except (ParserError,     # <body />
                        AssertionError,  # <html />
                        TypeError):      # xml
                    self.dom = lxml.html.document_fromstring(document)
        self.xpath_evaluator = XPathEvaluator(self.dom, extensions=extensions)

    def _clone(self, xpath, *args, **kwargs):
        return self.__class__(self.dom, xpath, *args, **kwargs)

    def __len__(self):
        return len(self.eval())

    def __eq__(self, other):
        my = self.eval()
        if isinstance(other, Ekskweri):
            other = other.eval()
        if len(my) != len(other):
            return False
        for el1, el2 in zip(my, other):
            if (isinstance(el1, lxml.html.HtmlElement) and
                isinstance(el2, lxml.html.HtmlElement)):
                if el1.tag() != el2.tag():
                    return False
                if sorted(el1.attrib().items()) != sorted(el2.attrib().items()):
                    return False
            elif isinstance(el1, basestring) and isinstance(el2, basestring):
                return unicode(el1) == unicode(el2)
            else:
                return NotImplemented
        return True

    @property
    def tag(self):
        return [el.tag for el in self.eval()]

    def eval(self):
        if not hasattr(self, '_value'):
            if self.xpath:
                try:
                    self._value = self.xpath_evaluator(self.xpath)
                except XPathEvalError, e:
                    raise XPathEvalError('%s: %s' % (e, self.xpath))
            else:
                self._value = [self.dom]
        return self._value

    def __repr__(self):
        def el_repr(el):
            if isinstance(el, lxml.html.HtmlElement):
                return tostring(el)
            elif isinstance(el, str):
                return el
            return repr(el)
        return repr([el_repr(el) for el in self.eval()])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __iter__(self):
        return iter(self.eval())
