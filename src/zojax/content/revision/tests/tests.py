##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" tests setup

$Id$
"""
import os, unittest, doctest
from zope import interface, schema
from zojax.content.revision.interfaces import IRevisions
from zojax.content.revision.revisions import Revisions
from zojax.content.type.item import PersistentItem
from zope.app.testing import functional
from zope.app.component.hooks import setSite
from zope.component.eventtesting import setUp as eventSetUp
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zojax.catalog.catalog import ICatalog, Catalog
from zojax.content.type.interfaces import IItemPublishing, IDraftedContent
from zope.schema.fieldproperty import FieldProperty


class IContent(interface.Interface):
    title = schema.TextLine(
        readonly=False,
        title=u'Test Title',
        description=u'Test content title.',
        default=u'',
        missing_value=u'',
        required=True)


class Content(PersistentItem, Revisions):
    interface.implements(IContent, IItemPublishing, IRevisions, IDraftedContent)

    __contentschema__ = IContent
    __contentfields__ = {'title': FieldProperty(IContent['title'])}


zojaxContentRevision = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxContentRevision', allow_teardown=True)


def FunctionalDocFileSuite(*paths, **kw):
    layer = zojaxContentRevision

    globs = kw.setdefault('globs', {})
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kwsetUp = kw.get('setUp')

    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        eventSetUp()

        root = functional.getRootFolder()
        setSite(root)
        sm = root.getSiteManager()

        # IIntIds
        root['ids'] = IntIds()
        sm.registerUtility(root['ids'], IIntIds)
        root['ids'].register(root)

        # catalog
        root['catalog'] = Catalog()
        sm.registerUtility(root['catalog'], ICatalog)

        # catalog
        root['content'] = Content()
        sm.registerUtility(root['content'], IContent)


    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')

    def tearDown(test):
        setSite(None)
        functional.FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old | doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


def test_suite():
    return unittest.TestSuite((
        FunctionalDocFileSuite("testbrowser.txt"),
    ))
