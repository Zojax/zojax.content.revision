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
import cgi
from difflib import SequenceMatcher

from zope import interface, component
from zope.schema import getFieldsInOrder
from zope.location import LocationProxy
from zope.component import getMultiAdapter
from zope.proxy import removeAllProxies
from zope.contentprovider.interfaces import IContentProvider
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces import NotFound
from zojax.content.actions.action import Action
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.revision.interfaces import IRevisions, IFieldDiff

from interfaces import _, IRevisionsAction


class ContentRevisionsAction(Action):
    component.adapts(IRevisions, interface.Interface)
    interface.implements(IRevisionsAction)

    weight = 1009
    title = _(u'Revisions')
    permission = 'zojax.ViewContentRevisions'

    @property
    def url(self):
        return '%s/revisions/'%absoluteURL(self.context, self.request)


class RevisionsView(object):

    title = _('Content revisions')

    def publishTraverse(self, request, name):
        try:
            return LocationProxy(
                self.context.getRevision(int(name)), self, name)
        except Exception, err:
            pass

        raise NotFound(self, request, name)

    def update(self):
        context = self.context
        request = self.request

        self.revisions = getMultiAdapter(
            (context, request, self), IContentProvider, 'content.revisions')
        self.revisions.update()

        if 'form.button.compare' in request:
            try:
                rev1 = context.getRevision(int(request['rev.id1']))
            except:
                rev1 = None

            try:
                rev2 = context.getRevision(int(request['rev.id2']))
            except:
                rev2 = None

            if rev1 is None or rev2 is None:
                IStatusMessage(request).add(
                    _('Please select revisions to compare.'), 'warning')

            else:
                self.rev1 = rev1
                self.rev2 = rev2

                results = []

                for name, field in getFieldsInOrder(
                    removeAllProxies(context).__contentschema__):

                    revField1 = field.bind(rev1)
                    revField2 = field.bind(rev2)

                    try:
                        diff1 = IFieldDiff(revField1)
                        diff2 = IFieldDiff(revField2)
                    except TypeError:
                        continue

                    source_value = revField1.query(rev1, field.default)
                    target_value = revField1.query(rev2, field.default)

                    if source_value is None or target_value is None:
                        continue

                    old = diff1.lines(source_value)
                    new = diff2.lines(target_value)

                    cruncher = SequenceMatcher(
                        isjunk=lambda x: x in u" \\t", a=old, b=new)

                    r = []
                    for tag, old_lo, old_hi, new_lo, new_hi in \
                            cruncher.get_opcodes():
                        if tag == u'replace':
                            r.append(
                                u'<span class="revision-diff-tag">%s</span>'%
                                u'changed:')

                            for line in old[old_lo:old_hi]:
                                r.append(
                                    u'<span class="revision-diff-removed'\
                                        '">%s</span>'%cgi.escape(line))
                            for line in new[new_lo:new_hi]:
                                r.append(
                                    u'<span class="revision-diff-added"'\
                                        '>%s</span>'%cgi.escape(line))
                        elif tag == u'delete':
                            r.append(
                                u'<span class="revision-diff-tag">%s</span>'%
                                u'removed:')
                            for line in old[old_lo:old_hi]:
                                r.append(
                                    u'<span class="revision-diff-removed"'\
                                        '>%s</span>'%cgi.escape(line))
                        elif tag == u'insert':
                            r.append(
                                u'<span class="revision-diff-tag">%s</span>'%
                                u'added:')
                            for line in new[new_lo:new_hi]:
                                r.append(
                                 u'<span class="revision-diff-added'\
                                     '">%s</span>'%cgi.escape(line))
                        elif tag == u'equal':
                            pass

                    results.append({'field': field, 'result': r})

                self.compared = results
