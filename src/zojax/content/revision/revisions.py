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
import sys, copy, pytz
from datetime import datetime
from persistent import Persistent
from BTrees.Length import Length
from BTrees.IOBTree import IOBTree
from rwproperty import setproperty, getproperty

from zope import interface, event
from zope.schema import getFields
from zojax.content.type.interfaces import IDraftedContent

from data import ContentRevisionType
from interfaces import IRevisions, IRevisionsManagement, \
    IWorkingContentRevision, ActiveRevisionChangedEvent


class RevisionsType(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Revisions' and \
                attrs['__module__'] == 'zojax.content.revision.revisions':
            return type.__new__(cls, name, bases, attrs)

        schema = attrs.get('__contentschema__')
        if schema is None:
            raise TypeError("__contentschema__ is required")

        # create content revision class
        ContentRevisionClass = ContentRevisionType(
            name, attrs.get('__contentclass__'),
            schema, attrs.get('__contentfields__', {}), attrs['__module__'])

        attrs['__contentclass__'] = ContentRevisionClass

        for f_id, field in getFields(schema).items():
            attrs[f_id] = ContentProperty(f_id)

        return type.__new__(cls, name, bases, attrs)


class Revisions(Persistent):
    interface.implements(IRevisions, IRevisionsManagement)

    __metaclass__ = RevisionsType

    _activeRevision = None
    _workingRevision = None

    _v_currentRevision = None

    def __init__(self, *args, **kw):
        super(Revisions, self).__init__(*args, **kw)

        self._revisions = IOBTree()
        self._revisions_length = Length(0)

    @property
    def revisions(self):
        return self._revisions.values()

    def getRevision(self, idx):
        return self._revisions[idx]

    def setRevision(self, idx):
        self._revisions[idx]
        self._activeRevision = idx

    def createRevision(self, revId=None):
        idx = self._revisions_length()

        revision = self.__contentclass__(idx, self)
        if idx:
            if revId is None:
                revId = self._activeRevision
            if revId is None:
                oldrevision = self._revisions[idx-1]
            else:
                oldrevision = self._revisions[revId]

            for f_id in getFields(self.__contentschema__):
                setattr(revision,f_id,copy.deepcopy(getattr(oldrevision,f_id)))

        revision.__date__ = datetime.now(pytz.utc)

        return revision

    def publishWorkingRevision(self):
        revision = self._workingRevision

        interface.noLongerProvides(revision, IWorkingContentRevision)

        idx = self._revisions_length()
        revision.__name__ = idx

        self._revisions[idx] = revision
        self._revisions_length.change(1)

        self._activeRevision = idx
        self._workingRevision = None

        event.notify(ActiveRevisionChangedEvent(self, idx))

    @property
    def activeRevision(self):
        if self._activeRevision is None:
            return self.workingRevision

        return self._revisions[self._activeRevision]

    @getproperty
    def activeRevisionId(self):
        return self._activeRevision

    @property
    def workingRevision(self):
        if self._workingRevision is None:
            self._workingRevision = self.createRevision()
            interface.alsoProvides(IWorkingContentRevision)

        return self._workingRevision


class ContentProperty(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, inst, klass):
        if IDraftedContent.providedBy(inst) or \
                inst._v_currentRevision == -1:
            return getattr(inst.workingRevision, self.name)

        if inst._v_currentRevision is not None:
            revision = inst._revisions[inst._v_currentRevision]
            return getattr(revision, self.name)

        return getattr(inst.activeRevision, self.name)

    def __set__(self, inst, value):
        if IDraftedContent.providedBy(inst) or inst.__parent__ is None:
            return setattr(inst.workingRevision, self.name, value)

        raise AttributeError('Field "%s" is read-only.'%self.name)
