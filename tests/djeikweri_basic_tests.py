from os.path import join, dirname
from nose.tools import ok_, eq_
from elkweri.djeikweri import Djeikweri, Element
from lxml.etree import tostring

def same_html(kweri, html):
    eq_(''.join(tostring(e) for e in kweri.eval()), html)

def same(a, b, msg='Not equal'):
    eq_(len(a), len(b), '%s: length mismatch %d != %d' % (msg, len(a), len(b)))
    for itema, itemb in zip(a, b):
        eq_(itema, itemb, '%s: %r != %r' % (msg, itema, itemb))

def test_appendTo_piece_by_piece():
    jQuery = Djeikweri('<html><body /></html>')
    para = jQuery('<a id="a1"/>')
    same_html(para, '<a id="a1"/>')
    ok_(para.created_from is jQuery)
    target = para.created_from('body')
    same_html(target, '<body/>')
    target.eval()[0].append(para.dom)
    same_html(target, '<body><a id="a1"/></body>')
    same_html(jQuery, '<html><body><a id="a1"/></body></html>')
    ok_(jQuery('#a1'))
    eq_(jQuery('#a1').length, 1)
    eq_(jQuery('#a1')[0].id, 'a1')

def test_appendTo():
    jQuery = Djeikweri('<html><body /></html>')
    para = jQuery('<a id="a1"/>')
    same_html(para, '<a id="a1"/>')
    ok_(para.created_from is jQuery)
    para.appendTo('body')
    same_html(jQuery, '<html><body><a id="a1"/></body></html>')

def test_remove():
    jQuery = Djeikweri('<html><body /></html>')
    para = jQuery('<a id="a1"/>').appendTo('body')
    para.remove()
    same_html(jQuery, '<html><body/></html>')

def test_multiple_classes():
    jQuery = Djeikweri('<html><body class="a b"/></html>')
    eq_(jQuery('.a.b').xpath,
        '//*[has_word(@class, "a")][has_word(@class, "b")]')

def test_sandbox():
    """Used for ongoing work"""
    jQuery = Djeikweri('<html/>')
    div = Element('div')
    div.innerHTML = '<a id="a1"/>'
    eq_(tostring(div.element), '<div><a id="a1"/></div>')
    eq_(tostring(jQuery("a", div).dom), '<div><a id="a1"/></div>')
    eq_( jQuery("a", div).xpath, '//a')
    eq_( jQuery("a", div).eval(), [div.firstChild])
    eq_( jQuery("a", div).get().xpath, '//a/@id')
    ok_(isinstance(div.firstChild, Element))
    eq_( jQuery("a", div).length, 1)
    eq_( jQuery("a", div).get().eval()[0], div.firstChild)
    ## This test still unsupported:
    #eq_( jQuery("a", div).get(), [div.firstChild], "Finding a second class." )
