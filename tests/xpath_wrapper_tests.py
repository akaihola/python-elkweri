from unittest import TestCase
from nose.tools import eq_
from elkweri.xpath_wrapper import make_filters, Ekskweri, XPathStep

class MakeFiltersTests(TestCase):
    def test_make_empty_filters(self):
        eq_(make_filters({}), '')

    def test_make_many_filters(self):
        eq_(make_filters({'id': 'id', 'other': 'other', 'class': 'class'}),
            '[@class="class"][@id="id"][@other="other"]')

class EkskweriTests(TestCase):
    def setUp(self):
        self.query = Ekskweri('<html id="h"><body id="b"/></html>')

    def test_descendant_xpath(self):
        q = self.query.descendant(XPathStep('body'))
        eq_(q.xpath, '//body')

    def test_descendant(self):
        q = self.query.descendant(XPathStep('body')).getattr('id')
        eq_(q.xpath, '//body/@id')
        eq_(q, ['b'])

    def test_iteration(self):
        q = self.query.descendant(XPathStep('body')).getattr('id')
        eq_(zip(q, [None]), [('b', None)])
