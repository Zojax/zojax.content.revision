##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
from BTrees.Length import Length
from BTrees.IOBTree import IOBTree

from zope import interface
from zope.schema import getFields
from zope.app.zopeappgenerations import getRootFolder
from zope.dublincore.interfaces import ICMFDublinCore
from zojax.content.revision.interfaces import IRevisions

def evolve(context):
    root = getRootFolder(context)

    for content in findObjectsMatching(root, IRevisions.providedBy):
        content._p_activate
        schema = content.__contentclass__.__schema__

        changed = False
        if not hasattr(content, '_revisions'):
            changed = True
            content._revisions = IOBTree()
            content._revisions_length = Length(0)

        for name, field in getFields(schema).items():
            if name in content.__dict__:
                setattr(content.workingRevision, name, content.__dict__[name])
                del content.__dict__[name]
                changed = True
            elif name in ('title', 'description'):
                dc = ICMFDublinCore(content)
                val = getattr(dc, name, '')
                if val:
                    setattr(content.workingRevision, name, val)

        if changed:
            content.publishWorkingRevision()
            content._p_changed = True


def findObjectsMatching(root, condition):
    if condition(root):
        yield root

    if hasattr(root, 'values') and callable(root.values):
        for subobj in root.values():
            for match in findObjectsMatching(subobj, condition):
                yield match
