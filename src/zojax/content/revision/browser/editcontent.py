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
from zope import interface, event
from zope.schema import getFieldNames
from zope.component import getAdapters
from zope.security import checkPermission
from zope.security.checker import canWrite
from zope.security.proxy import removeSecurityProxy
from zope.cachedescriptors.property import Lazy
from zope.lifecycleevent import ObjectModifiedEvent

from zojax.wizard.step import WizardStepForm
from zojax.wizard.interfaces import ISaveable
from zojax.layoutform import Fields, PageletEditSubForm
from zojax.layoutform.interfaces import IPageletSubform
from zojax.content.type.interfaces import IContentType
from zojax.content.forms.interfaces import _, IContentStep
from zojax.content.revision.interfaces import IContentRevision


class ContentStep(WizardStepForm):
    interface.implements(ISaveable, IContentStep)

    name = 'content'
    title = _('Content')
    label = _('Modify content')

    @Lazy
    def fields(self):
        return Fields(self.getContent().__schema__, IContentRevision)

    def _loadSubforms(self):
        return [(name, form) for name, form in getAdapters(
                (self.context, self, self.request), IPageletSubform)]

    def isAvailable(self):
        if not checkPermission('zojax.ModifyContent', self.getContent()):
            return False

        if not (self.groups or self.subforms or self.forms or self.views):
            return bool(self.fields)

        return super(ContentStep, self).isAvailable()

    def applyChanges(self, data):
        note = data['__note__'] or u''
        del data['__note__']

        changes = super(ContentStep, self).applyChanges(data)
        if changes:
            content = self.getContent()
            content.__note__ = note
            self.context.publishWorkingRevision()
            event.notify(ObjectModifiedEvent(self.context))

        return changes

    def getContent(self):
        return removeSecurityProxy(self.context).workingRevision


class ContentBasicFields(PageletEditSubForm):

    def isAvailable(self):
        return False
