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
from zope import interface, schema
from zope.i18nmessageid import MessageFactory
from zope.component.interfaces import IObjectEvent, ObjectEvent

_ = MessageFactory('zojax.content.revision')


class IRevisions(interface.Interface):
    """ content with revisions """

    revisions = interface.Attribute('Revisions')
    activeRevision = interface.Attribute('Active content revision')
    activeRevisionId = interface.Attribute('Active content revision id')
    workingRevision = interface.Attribute('Working content revision')

    __contentclass__ = interface.Attribute('Content revision class')
    __contentschema__ = interface.Attribute('Content revision schema')
    __contentfields__ = interface.Attribute('Custom content revision fields')

    def getRevision(revId):
        """ return revision object """


class IRevisionsManagement(interface.Interface):
    """ revisions management """

    def setRevision(revId):
        """ set active revision """

    def createRevision(revId=None):
        """ create new revision, copy data from revId """

    def removeWorkingRevision():
        """ remove working content """

    def publishWorkingRevision():
        """ publish working content """


class IContentRevision(interface.Interface):
    """ content revision object for revisions """

    __schema__ = interface.Attribute('Revision schema')

    __date__ = interface.Attribute('Date')

    __principal__ = interface.Attribute('Principal')

    __note__ = schema.TextLine(
        title = _('Modification note'),
        default = u'',
        required = False)


class IFieldDiff(interface.Interface):
    """ field diff """

    def lines(context):
        """ return lines """


class IWorkingContentRevision(interface.Interface):
    """ working content revision """


class IActiveRevisionChangedEvent(IObjectEvent):
    """ active revision changed event """

    revid = interface.Attribute('Revision id')


class ActiveRevisionChangedEvent(ObjectEvent):
    interface.implements(IActiveRevisionChangedEvent)

    def __init__(self, object, revid):
        self.object = object
        self.revid = revid
