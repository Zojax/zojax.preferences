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
from zope.component import getUtility
from zope.app.component.interfaces import ISite
from zope.security.interfaces import Unauthorized
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from zojax.preferences.interfaces import IPreferenceGroup


@component.adapter(ISite, interface.Interface)
def getPreferences(site, request):
    rootGroup = getUtility(IPreferenceGroup)
    rootGroup = rootGroup.__bind__()

    if IUnauthenticatedPrincipal.providedBy(rootGroup.__principal__):
        raise Unauthorized('preferences')

    if rootGroup.isAvailable():
        return rootGroup
    else:
        return None
