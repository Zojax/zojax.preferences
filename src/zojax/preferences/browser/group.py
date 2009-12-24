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
""" IPreferenceGroup view

$Id$
"""
from zope import schema
from zope.security import checkPermission
from zope.security.interfaces import Unauthorized
from zope.cachedescriptors.property import Lazy
from zojax.layoutform import Fields, PageletEditForm


class PreferenceGroup(object):

    def update(self):
        if not checkPermission(self.context.__permission__, self.context):
            raise Unauthorized()

        context = self.context
        request = self.request

        subgroups = []

        for name, group in context.items():
            if not group.isAvailable():
                continue
            subgroups.append(group)

        self.subgroups = subgroups
        self.hasFields = bool(schema.getFields(self.context.__schema__))

        if not self.hasFields and len(subgroups) == 1:
            self.oneSubgroup = True
        else:
            self.oneSubgroup = False

        self.render = self.render()


class PreferenceGroupView(PageletEditForm):

    @property
    def prefix(self):
        return str(self.context.__id__)

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    @Lazy
    def fields(self):
        return Fields(self.context.__schema__, omitReadOnly=True)

    def update(self):
        if not checkPermission(self.context.__permission__, self.context):
            raise Unauthorized()

        super(PreferenceGroupView, self).update()
