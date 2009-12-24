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

  >>> from zope import interface
  >>> from zope.security.interfaces import IPrincipal, IGroup
  >>> class P(object):
  ...   interface.implements(IPrincipal)

  >>> class Prefs(object):
  ...     __principal__ = None

  >>> prefs = Prefs()
  >>> prefs.__principal__ = P()

  >>> import utils
  >>> print utils.isUser(prefs)
  True
  >>> print utils.isGroup(prefs)
  False

  >>> interface.directlyProvides(prefs.__principal__, IGroup)
  >>> print utils.isUser(prefs)
  False
  >>> print utils.isGroup(prefs)
  True
  >>> print utils.isMemberAwareGroup(prefs)
  False
"""
from zope import interface
from zope.schema import getFieldNames
from zope.security import checkPermission
from zope.security.checker import canWrite
from zope.security.interfaces import IPrincipal, IGroup, IMemberAwareGroup


def isUser(group):
    principal = group.__principal__
    return IPrincipal.providedBy(principal) and not IGroup.providedBy(principal)


def isGroup(group):
    return IGroup.providedBy(group.__principal__)


def isMemberAwareGroup(group):
    return IMemberAwareGroup.providedBy(group.__principal__)


def hasEditableFields(group):
    for name in getFieldNames(group.__schema__):
        if canWrite(group, name):
            return True

    return False


class PrincipalChecker(object):

    def __init__(self, iface):
        self.iface = iface

    def __call__(self, group):
        return self.iface.providedBy(group.__principal__)


def PermissionChecker(prefs):
    return checkPermission(prefs.__permission__, prefs)
