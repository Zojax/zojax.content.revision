##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""

$Id$
"""
from itertools import chain
from zope import interface, component
from zope.schema.interfaces import IText, ITextLine, ICollection
try:
    from zojax.richtext.interfaces import IRichText
except ImportError:
    class IRichText(interface.Interface): pass

from interfaces import IFieldDiff


class TextDiff(object):
    interface.implements(IFieldDiff)
    component.adapts(IText)

    def __init__(self, field):
        pass

    def lines(self, value):
        return value.split(u'\n')


class TextLineDiff(object):
    interface.implements(IFieldDiff)
    component.adapts(ITextLine)

    def __init__(self, field):
        pass

    def lines(self, value):
        return (unicode(value),)


class CollectionDiff(object):
    component.adapts(ICollection)
    interface.implements(IFieldDiff)

    def __init__(self, field):
        self.field = field

    def lines(self, value):
        diff = IFieldDiff(self.field.value_type, TextLineDiff(field))
        return tuple(chain(*[diff.lines(v) for v in value]))


class RichTextDiff(object):
    component.adapts(IRichText)
    interface.implements(IFieldDiff)

    def __init__(self, field):
        pass

    def lines(self, value):
        return value.text.split(u'\n')
