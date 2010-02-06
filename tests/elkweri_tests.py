# -*- coding: utf-8 -*-

from os.path import join, dirname
from unittest import TestCase
from nose.tools import eq_, ok_, assert_raises

DATA_DIR = join(dirname(__file__), 'data')

from elkweri.tags import *

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

from elkweri import Elkweri

class HtmlTests(TestCase):
    html = Elkweri(u'<html><body><div id="main">'
                   u'<p class="para" id="para1">This</p>'
                   u'<p class="para" id="para2">is '
                   u'<span class="inner"><a href="link">a</a></span></p>'
                   u'<p class="lastpara" id="para3">test'
                   u'<span class="inner">kin</span></p>'
                   u'</div></body></html>')

    def test_many_descendants_xpath(self):
        eq_((self.html // p).xpath, '//p')

    def test_many_descendants_boolean(self):
        ok_(self.html // p)

    def test_many_descendants_length(self):
        eq_(len(self.html // p), 3)

    def test_many_descendants_tags(self):
        eq_((self.html // p).tag, ['p', 'p', 'p'])

    def test_one_descendant_boolean(self):
        ok_(self.html // div)

    def test_one_descendant_length(self):
        eq_(len(self.html // div), 1)

    def test_one_descendant_tag(self):
        eq_((self.html // div).tag, ['div'])

    def test_direct_descendants_xpath(self):
        eq_((self.html // div / p).xpath, '//div/p')

    def test_direct_descendants_length(self):
        eq_(len(self.html // div / p), 3)

    def test_direct_descendants_tags(self):
        eq_((self.html // div / p).tag, ['p', 'p', 'p'])

    def test_by_tag_and_id_xpath(self):
        eq_((self.html // div('#main')).xpath, '//div[@id="main"]')

    def test_by_tag_and_id_boolean(self):
        ok_(self.html // div('#main'))

    def test_by_class_xpath(self):
        eq_((self.html // x('.para')).xpath, '//*[has_word(@class, "para")]')

    def test_by_class_boolean(self):
        ok_(self.html // x('.para'))

    def test_by_id_and_class_xpath(self):
        eq_((self.html // x('#para2', '.lastpara')).xpath,
            '//*[has_word(@class, "lastpara")][@id="para2"]')

    def test_by_id_and_class_boolean(self):
        ok_(self.html // x('#para3', '.lastpara'))

    def test_following_siblings_xpath(self):
        eq_((self.html // p ^ p).xpath, '//p/following-sibling::p')

    def test_following_siblings_length(self):
        eq_(len(self.html // p ^ p), 2)

    def test_following_siblings_tag(self):
        eq_((self.html // p ^ p).tag, ['p', 'p'])

    def test_following_siblings_class(self):
        eq_((self.html // p ^ p)['class'], ['para', 'lastpara'])

    def test_following_siblings_id(self):
        eq_((self.html // p ^ p)['id'], ['para2', 'para3'])

    def test_following_sibling_xpath(self):
        eq_((self.html // x('#para1') + p).xpath,
            '//*[@id="para1"]/following-sibling::p[1]')

    def test_following_sibling_length(self):
        eq_(len(self.html // x('#para1') + p), 1)

    def test_following_sibling_tag(self):
        eq_((self.html // x('#para1') + p).tag, ['p'])

    def test_following_sibling_class(self):
        eq_((self.html // x('#para1') + p)['class'], ['para'])

    def test_following_sibling_id(self):
        eq_((self.html // x('#para1') + p)['id'], ['para2'])

    def test_containing_children(self):
        eq_((self.html // p < span).tag, ['p', 'p'])

    def test_containing_grandchild_xpath(self):
        eq_(((self.html // p) < (span / a)).xpath, '//p[span/a]')

    def test_containing_grandchild_tags(self):
        eq_((self.html // p < (span / a)).tag, ['p'])

    def test_union_xpath(self):
        eq_((self.html // p < (span / a))
            .union(self.html // p).xpath, '(//p[span/a]|//p)')

    def test_id_of_union_xpath(self):
        eq_((self.html // p < (span / a))
            .union(self.html // p)['id'].xpath, '(//p[span/a]|//p)/@id')

    def test_union_fails_if_non_root(self):
        """Union can't be used except at the beginning of an expression"""
        assert_raises(SyntaxError, lambda: self.html // x // (span.union(a)))

class FormTests(TestCase):
    form1 = Elkweri(
        u'<form method="post" action=".">'
        u'<input type="text" name="last_name" id="id_last_name" value="Ek" />'
        u'<input type="submit" value="Send" />'
        u'</form>') / html / body / form

    def test_form_boolean(self):
        ok_(self.form1)

    def test_form_tag(self):
        eq_(self.form1.tag, ['form'])

    def test_form_has_inputs(self):
        ok_(self.form1 / input)

    def test_form_number_of_inputs(self):
        eq_(len(self.form1 / input), 2)

    def test_form_first_input(self):
        ok_(self.form1 / input(name='last_name', id='id_last_name', value='Ek'))

    def test_form_nonexistent_input(self):
        ok_(not self.form1 / input(
            name='last_name', id='id_last_name', value='Ahl'))

    def test_form_submit(self):
        ok_(self.form1 / input(type='submit', value='Send'))

    def test_form_input_tags(self):
        eq_((self.form1 / input).tag, ['input', 'input'])

    def test_form_first_input_by_id(self):
        ok_(self.form1 / input[0]('#id_last_name'))

    def test_form_nonexistent_input_by_id(self):
        ok_(self.form1 / input('#id_last_name')[0])
        ok_(not self.form1 / input[0]('#id_first_name'))
        ok_(not self.form1 / input('#id_first_name')[0])

def test_root_id():
    html1 = Elkweri(file(join(DATA_DIR, 'jquery_test.html')).read())
    eq_((html1 / html)['id'], ['html'])
