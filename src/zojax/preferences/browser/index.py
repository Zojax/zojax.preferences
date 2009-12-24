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
from zope.interface import Interface
from zope.component import getUtility
from zope.security import checkPermission
from zojax.preferences.utils import hasEditableFields
from zojax.preferences.interfaces import IPreferenceGroup, IPreferenceCategory


class PreferencesView(object):

    def groups(self):
        root = self.context
        request = self.request

        groups = []
        for name, group in root.items():
            if not group.isAvailable():
                continue

            if IPreferenceCategory.providedBy(group):
                subgroups = [(sgroup.__title__,
                              sgroup.__id__.split('.')[-1], sgroup)
                             for t, sgroup in group.items()
                             if sgroup.isAvailable()]
                if (len(subgroups) > 1) or hasEditableFields(group):
                    groups.append((group.__title__, group,
                                   [{'id': id, 'group': sgroup}
                                    for t, id, sgroup in subgroups]))
                elif len(subgroups) == 1:
                    groups.append((group.__title__, group, ()))
            else:
                groups.append((group.__title__, group, ()))

        return [{'group':group, 'subgroups': groups}
                for t, group, groups in groups]
