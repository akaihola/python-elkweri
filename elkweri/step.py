from xpath_wrapper import XPathStep

class Step(XPathStep):
    "The Step class represents one step in an XPath expression"

    __floordiv__ = XPathStep.descendant
    __div__ = XPathStep.child
    __truediv__ = XPathStep.child
    __lt__ = XPathStep.has_child
    __add__ = XPathStep.next
    __xor__ = XPathStep.following
    __or__ = XPathStep.union

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

