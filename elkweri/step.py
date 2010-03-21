from xpath_wrapper import XPathStep

class Step(XPathStep):
    "The Step class represents one step in an XPath expression"

    __floordiv__ = XPathStep.descendant
    __rfloordiv__ = XPathStep.reverse(__floordiv__)
    __div__ = XPathStep.child
    __rdiv__ = XPathStep.reverse(__div__)
    __truediv__ = XPathStep.child
    __rtruediv__ = XPathStep.reverse(__truediv__)
    __lt__ = XPathStep.has_child
    __rlt__ = XPathStep.reverse(__lt__)
    __add__ = XPathStep.next
    __radd__ = XPathStep.reverse(__add__)
    __xor__ = XPathStep.following
    __rxor__ = XPathStep.reverse(__xor__)
    __or__ = XPathStep.union
    __ror__ = XPathStep.reverse(__or__)

    def __getitem__(self, index):
        "XPath [integer] and /@attribute"
        if isinstance(index, int):
            return self.eq(index)
        else:
            return self.getattr(index)

    def __call__(self, *args, **kwargs):
        result = self
        for arg in args:
            if arg.startswith('#'):
                kwargs['id'] = arg[1:]
            elif arg.startswith('.'):
                result = self.has_class(arg[1:])
            else:
                raise ValueError('#id or .class expected: %r' % arg)
        return result.attr(kwargs)

