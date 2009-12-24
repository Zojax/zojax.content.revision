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
import sys, pytz
from datetime import datetime
from persistent import Persistent

from zope import interface, component
from zope.proxy import removeAllProxies
from zope.schema import getFields
from zope.schema.fieldproperty import FieldProperty
from zope.security.management import queryInteraction
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.security.protectclass import protectName, protectSetAttribute

from interfaces import IContentRevision


class ContentRevisionType(type):

    def __new__(cls, name, klass, schema, fields, module):
        cname = 'ContentRevision<%s>'%name

        # generate bases
        if klass is None:
            klass = ContentRevision

        if issubclass(klass, ContentRevision):
            bases = (klass,)
        else:
            bases = (klass, ContentRevision)

        # generate fields
        attrs = {'__module__': module}
        for f_id in getFields(schema):
            if f_id in fields:
                attrs[f_id] = fields[f_id]
            else:
                attrs[f_id] = FieldProperty(schema[f_id])

        # create type
        tp = type.__new__(cls, cname, bases, attrs)

        # set schema and implements
        tp.__schema__ = SchemaProperty(schema)

        component.getSiteManager().registerAdapter(
            getContentRevision, (tp,), schema)

        # set class to module
        setattr(sys.modules[module], cname, tp)

        # create security checker
        for n, d in schema.namesAndDescriptions(1):
            protectName(tp, n, 'zope.View')

        for n, d in IContentRevision.namesAndDescriptions(1):
            protectName(tp, n, 'zope.View')

        protectName(tp, '__schema__', 'zope.Public')

        for name, field in getFields(schema).items() + \
                getFields(IContentRevision).items():
            if not field.readonly:
                protectSetAttribute(tp, name, 'zojax.ModifyContent')

        return tp


class SchemaProperty(object):

    def __init__(self, schema):
        self.schema = schema

    def __get__(self, inst, klass):
        return self.schema

    def __set__(self, inst, value):
        raise AttributeError("Can't set __schema__")


class ContentRevision(Persistent):
    interface.implements(IContentRevision)

    __note__ = u''
    __date__ = None
    __principal__ = None

    def __init__(self, name, parent):
        self.__name__ = name
        self.__parent__ = parent


def getContentRevision(revision):
    return revision


@component.adapter(IContentRevision, IObjectModifiedEvent)
def contentModifiedHandler(revision, event):
    revision = removeAllProxies(revision)
    revision.__date__ = datetime.now(pytz.utc)

    interaction = queryInteraction()

    if interaction is not None:
        for participation in interaction.participations:
            if participation is not None:
                revision.__principal__ = participation.principal.id
