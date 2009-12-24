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
""" custom IBreadcrumb implementation for IPreferencesGroup

$Id$
"""
from zope import interface, component
from zope.traversing.browser import absoluteURL
from z3c.breadcrumb.browser import GenericBreadcrumb
from zojax.preferences.interfaces import _, IPreferenceGroup


class PreferenceGroupBreadcrumb(GenericBreadcrumb):
    component.adapts(IPreferenceGroup, interface.Interface)

    @property
    def url(self):
        return '%s/'%(absoluteURL(self.context, self.request))

    @property
    def name(self):
        name = self.context.__title__ or self.context.__id__
        if not name:
            name = _(u'Preferences')
        return name
