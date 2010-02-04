import re
import lxml.html
from xpath_wrapper import XPathStep, Ekskweri
import lxml.etree

class Element(object):
    def __init__(self, item):
        if isinstance(item, lxml.etree._Element):
            self.element = item
        else:
            self.element = lxml.html.Element(item)

    @property
    def firstChild(self):
        return Element(self.element.getchildren()[0])

    def _set_inner_html(self, html):
        while True:
            children = self.element.getchildren()
            if not children:
                break
            self.element.remove(children.pop())
        self.element.append(lxml.html.fromstring(html))

    def _get_inner_html(self):
        return ''.join(etree.tostring(el) for el in self.element.getchildren())

    def __eq__(self, other):
        if isinstance(other, lxml.etree._Element):
            return self.element == other
        if isinstance(other, Ekskweri):
            return self.element == other.dom
        if isinstance(other, basestring):
            return str(self.element.attrib.get('id')) == str(other)
        return self.element == other.element

    innerHTML = property(_get_inner_html, _set_inner_html)

class Djeikweri(Ekskweri):
    def __call__(self, selector, context=None, **kwargs):
        result = self
        if context:
            if isinstance(context, Ekskweri):
                result = context
            elif isinstance(context, Element):
                result = self.__class__(context, **kwargs)
            else:
                result = result.jquery(context)
        if selector.startswith('<') and len(selector) > 2:
            # create a new jQuery object from HTML
            new_djeikweri = self.__class__(selector)
            new_djeikweri.created_from = self
            return new_djeikweri
        return result.jquery(selector)

    def jquery(self, selector):
        parts = re.split(r', *', selector)
        result = self.jquery_side(parts[0])
        for part in parts[1:]:
            result = result.union(self.jquery_side(part))
        return result

    def jquery_side(self, selector):
        result = self
        op = 'descendant'
        for step in selector.split():
            if step == '>':
                op = 'child'
                continue
            result = result.jquery_single(step, op)
            op = 'descendant'
        return result

    def jquery_single(self, selector, op):
        try:
            tag, rest = re.match(r'([a-zA-Z0-9_*]*)(.*)$', selector).groups()
        except AttributeError:
            raise SyntaxError('Invalid selector: %s' % selector)
        result = getattr(self, op)(XPathStep(tag or '*'))
        while rest:
            if not rest.startswith(('#', '.', ':', '[')):
                raise SyntaxError('Invalid selector: %s' % rest)
            match = re.search(r'(?<!\\)[#\.:[]', rest[1:])
            if match:
                part, rest = rest[:match.start()+1], rest[match.start()+1:]
            else:
                part, rest = rest.replace('\\', ''), ''
            if part.startswith(':'):
                if part == ':first':
                    result = result.eq(0)
                else:
                    raise SyntaxError('Invalid selector: %s' % unicode(part))
            elif part.startswith('['):
                try:
                    attname, op, val = re.match(r'\[([^\*=]*)'
                                                r'([\*=]*)'
                                                r'([^\*=]*)\]$', part).groups()
                except AttributeError:
                    raise SyntaxError('Invalid selector: %s' % part)
                if op == '*=':
                    result = result.attr({'%s__contains' % attname: val})
                elif op == '=':
                    result = result.attr({attname: val})
            elif part.startswith('#'):
                result = result.attr({'id': part[1:]})
            elif part.startswith('.'):
                result = result.has_class(part[1:])
            else:
                raise SyntaxError('Invalid selector: %s' % part)
        return result

    def get(self):
        return self.getattr('id')

    def find(self, selector):
        return self(selector)

    def __getitem__(self, index):
        return self.eq(index)

    @property
    def id(self):
        if len(self) != 1:
            raise ValueError("Can only get id of a single tags, got %d"
                             % len(self))
        return self.getattr('id').eval()[0]

    size = lambda self: len(self)
    @property
    def length(self):
        return len(self)

    def appendTo(self, selector):
        target = self.created_from(selector)
        if len(target) != 1:
            raise ValueError('appendTo must have a unique target')
        target_node = target.eval()[0]
        target_node.append(self.dom)
        self.appended_to = target_node
        return self

    def remove(self):
        self.appended_to.remove(self.dom)
