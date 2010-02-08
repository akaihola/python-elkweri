from unittest import TestCase
from nose.tools import eq_
from elkweri.tags import p
from elkweri.step import Step


class StepTests(TestCase):

    def test_simple_step(self):
        eq_(p.xpath, 'p')

    def test_descendants(self):
        eq_((p // p).xpath, 'p//p')

    def test_children(self):
        eq_((p / p).xpath, 'p/p')

    def test_grandchildren(self):
        eq_((p / p / p).xpath, 'p/p/p')

    def test_grand_grandchildren(self):
        eq_((p / p / p / p).xpath, 'p/p/p/p')

    def test_has_descendants(self):
        eq_((p < p).xpath, 'p[p]')

    def test_next_sibling(self):
        eq_((p + p).xpath, 'p/following-sibling::p[1]')

    def test_following_siblings(self):
        eq_((p ^ p).xpath, 'p/following-sibling::p')

    def test_child_index(self):
        eq_(p[0].xpath, 'p[1]')

    def test_by_id(self):
        eq_(p('#id').xpath, 'p[@id="id"]')

    def test_by_class(self):
        eq_(p('.class').xpath, 'p[has_word(@class, "class")]')

    def test_by_multiple_attributes(self):
        eq_(p('.class', '#id', other='other').xpath,
            'p[has_word(@class, "class")][@id="id"][@other="other"]')

    def test_union(self):
        eq_((p.union(Step('q'))).xpath, '(p|q)')

    def test_union_operator(self):
        eq_((p | Step('q')).xpath, '(p|q)')
