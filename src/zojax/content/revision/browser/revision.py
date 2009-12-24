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
from zope import interface, component, event
from zope.i18n import translate
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.component import getMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectModifiedEvent
from z3c.breadcrumb.browser import GenericBreadcrumb
from zojax.content.actions.action import Action
from zojax.content.actions.interfaces import IActionsContext
from zojax.content.type.interfaces import IContentView
from zojax.content.revision.interfaces import IContentRevision
from zojax.statusmessage.interfaces import IStatusMessage

from interfaces import _, IWorkingRevisionAction


@component.adapter(IContentRevision)
@interface.implementer(IActionsContext)
def ActionsContext(context):
    return context.__parent__.__parent__


class ContentRevision(object):

    def update(self):
        request = self.request
        content = self.content

        self.modify = checkPermission('zojax.ModifyContent', content)

        if self.modify and 'form.button.makeactive' in request:
            content.setRevision(self.revid)
            event.notify(ObjectModifiedEvent(content))
            IStatusMessage(request).add(_('Revision has been activated.'))

        view = getMultiAdapter((content, request), IContentView)
        view.update()
        self.contentView = view

        self.revidtitle = '%0.3d'%self.revid
        self.active = content.activeRevisionId == self.revid

    def __call__(self):
        revid = int(self.context.__name__)
        content = self.context.__parent__.__parent__

        self.revid = revid
        self.content = content

        removeAllProxies(content)._v_currentRevision = revid

        rendered = super(ContentRevision, self).__call__()

        removeAllProxies(content)._v_currentRevision = None

        return rendered


class ContentRevisionBreadcrumb(GenericBreadcrumb):
    component.adapts(IContentRevision, interface.Interface)

    @property
    def name(self):
        return u'Revision %0.3d'%int(self.context.__name__)

    @property
    def url(self):
        return '%s/'%absoluteURL(self.context, self.request)


class ActivateRevision(object):

    def __call__(self):
        revid = int(self.context.__name__)
        content = self.context.__parent__.__parent__

        if checkPermission('zojax.ModifyContent', content):
            removeAllProxies(content).setRevision(revid)
            IStatusMessage(self.request).add(
                _('Revision has been activated.'))

        self.redirect('../')
