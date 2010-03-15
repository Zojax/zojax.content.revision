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
from zope.security import checkPermission
from zope.component import getUtility, queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.table.table import Table
from zojax.table.column import Column, AttributeColumn
from zojax.formatter.utils import getFormatter
from zojax.content.table.author import AuthorNameColumn
from zojax.content.revision.interfaces import IRevisions

from interfaces import _, IRevisionsTable


class RevisionsTable(Table):
    interface.implements(IRevisionsTable)
    component.adapts(IRevisions, interface.Interface, interface.Interface)

    title = _('Revisions')

    pageSize = 15
    enabledColumns = ('rev1', 'rev2', 'id', 'principal', 'date','note','active')
    msgEmptyTable = _('No revisions.')
    cssClass = 'z-table z-content-revisions'

    def initDataset(self):
        self.dataset = list(self.context.revisions)
        self.dataset.reverse()

    def update(self):
        super(RevisionsTable, self).update()

        self.allowModify = checkPermission('zojax.ModifyContent', self.context)


class IdColumn(Column):
    component.adapts(interface.Interface, interface.Interface, IRevisionsTable)

    name = 'id'
    title = _('Rev Id')
    cssClass = 'ctb-revision-revid'
    attrName = '__name__'

    def query(self, default=None):
        return '%0.3d'%int(self.content.__name__)

    def render(self):
        return u'<a href="%s/revisions/%0.3d/">%0.3d</a>'%(
            absoluteURL(self.context, self.request),
            self.content.__name__, self.content.__name__)


class PrincipalColumn(AuthorNameColumn):
    component.adapts(interface.Interface, interface.Interface, IRevisionsTable)

    title = _('User')
    cssClass = 'ctb-revisioin-principal'

    def getPrincipal(self, content):
        return self.content.getPrincipal()


class DateColumn(AttributeColumn):
    component.adapts(interface.Interface, interface.Interface, IRevisionsTable)

    name = 'date'
    title = _('Date')
    cssClass = 'ctb-revisioin-date'
    attrName = '__date__'

    def update(self):
        super(DateColumn, self).update()

        self.table.environ['fancyDatetime'] = getFormatter(
            self.request, 'fancyDatetime', 'short')

    def render(self):
        value = self.query()
        if value:
            return self.globalenviron['fancyDatetime'].format(value)

        return u'---'


class NoteColumn(AttributeColumn):
    component.adapts(interface.Interface, interface.Interface, IRevisionsTable)

    name = 'note'
    title = _('Note')
    cssClass = 'ctb-revision-note'
    attrName = '__note__'


class ActiveColumn(Column):
    component.adapts(interface.Interface, interface.Interface, IRevisionsTable)

    name = 'active'
    title = _('Status')
    cssClass = 'ctb-revision-status'

    def render(self):
        if self.context.activeRevisionId == self.content.__name__:
            return u'Active'

        if self.table.allowModify:
            return u'---- <a href="%s/revisions/%0.3d/activate.html" '\
                u'title="Activate">?</a>'%(
                absoluteURL(self.context, self.request), self.content.__name__)
        else:
            return u'----'


class Rev1Column(Column):
    component.adapts(interface.Interface, interface.Interface, IRevisionsTable)

    name = 'rev1'
    title = u''
    cssClass = 'z-table-cell-min'

    def render(self):
        return u'<input type="radio" name="rev.id1" value="%s" />'%(
            self.content.__name__)


class Rev2Column(Column):
    component.adapts(interface.Interface, interface.Interface, IRevisionsTable)

    name = 'rev2'
    title = u''
    cssClass = 'z-table-cell-min'

    def render(self):
        return u'<input type="radio" name="rev.id2" value="%s" />'%(
            self.content.__name__)
