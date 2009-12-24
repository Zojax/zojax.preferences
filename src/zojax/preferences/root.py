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
""" Root Preference Group

$Id$
"""
from zope import interface
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from preference import PreferenceGroup
from interfaces import _, IBound, IRootPreferences, IPreferenceCategory


class PersonalPreferences(PreferenceGroup):
    interface.implements(IRootPreferences, IPreferenceCategory)

    __id__ = ''
    __name__ = u'preferences'
    __title__ = _(u'Personal preferences')
    __description__ = _('This area allows you to change personal preferences.')
    __schema__ = IRootPreferences
    __principal__ = None

    def __init__(self):
        self.__subgroups__ = ()

    def __bind__(self, principal=None, parent=None):
        if parent is None:
            parent = getSite()
        return super(PersonalPreferences, self).__bind__(principal, parent)

    def isAvailable(self):
        if (not IBound.providedBy(self) or
            IUnauthenticatedPrincipal.providedBy(self.__principal__)):
            return False
        return True
