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
from zope.app.security.settings import Allow, Unset
from zope.securitypolicy.interfaces import IPrincipalRoleMap

from interfaces import IBound


class PreferenceGroupRoles(object):
    component.adapts(IBound)
    interface.implements(IPrincipalRoleMap)

    def __init__(self, context):
        self.pid = context.__principal__.id

    def getPrincipalsForRole(self, role_id):
        if (role_id == 'preference.Owner'):
            return ((self.pid, Allow),)
        else:
            return ()

    def getRolesForPrincipal(self, principal_id,
                             allow = (('preference.Owner', Allow),)):
        if principal_id == self.pid:
            return allow
        else:
            return ()

    def getSetting(self, role_id, principal_id):
        if (principal_id == self.pid) and (role_id == 'preference.Owner'):
            return Allow
        else:
            return Unset

    def getPrincipalsAndRoles(self):
        return ()
