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
from zope import interface, component
from zope.proxy import removeAllProxies
from zope.component import getMultiAdapter
from zope.traversing.browser import absoluteURL
from zojax.content.actions.action import Action
from zojax.content.type.interfaces import IContentView
from zojax.content.revision.interfaces import IRevisions
from zojax.statusmessage.interfaces import IStatusMessage

from interfaces import _, IWorkingRevisionAction


class WorkingRevisionAction(Action):
    component.adapts(IRevisions, interface.Interface)
    interface.implements(IWorkingRevisionAction)

    weight = 1010
    title = _(u'Working Revision')
    permission = 'zojax.ModifyContent'

    @property
    def url(self):
        return '%s/workingrevision.html'%absoluteURL(self.context, self.request)


class WorkingRevision(object):

    def update(self):
        request = self.request

        if 'form.buttons.publish' in request:
            self.context.publishWorkingRevision()
            IStatusMessage(request).add(_('Revision has been published.'))
            self.redirect('.')
            return

        view = getMultiAdapter((self.context, self.request), IContentView)
        view.update()
        self.contentView = view

    def __call__(self):
        context = self.context
        removeAllProxies(context)._v_currentRevision = -1

        rendered = super(WorkingRevision, self).__call__()

        removeAllProxies(context)._v_currentRevision = None

        return rendered
