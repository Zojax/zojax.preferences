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
from zope import interface
from zope.cachedescriptors.property import Lazy
from zope.interface.common.mapping import IEnumerableMapping
from zope.security.management import getInteraction
from zope.component import queryUtility, getMultiAdapter, getGlobalSiteManager

from interfaces import UnboundPreferenceGroup
from interfaces import IPreferenceGroup, IBound, IDataStorage

_marker = object()


class PreferenceGroup(object):
    interface.implements(IPreferenceGroup, IEnumerableMapping)

    __principal__ = None

    def __init__(self, tests=()):
        self.__name__ = self.__id__.rsplit('.', 1)[-1]
        self.__tests__ = tests
        self.__subgroups__ = ()

    def __bind__(self, principal=None, parent=None):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)

        # set parent
        clone.__parent__ = parent

        # set principal
        if principal is None:
            if IBound.providedBy(parent):
                clone.__principal__ = parent.__principal__
            else:
                clone.__principal__ = getInteraction().participations[0].principal
        else:
            clone.__principal__ = principal

        interface.alsoProvides(clone, IBound)
        return clone

    @Lazy
    def data(self):
        if not IBound.providedBy(self):
            raise UnboundPreferenceGroup()

        return getMultiAdapter((self.__principal__, self), IDataStorage)

    def isAvailable(self):
        if IPreferenceGroup.providedBy(self.__parent__):
            if not self.__parent__.isAvailable():
                return False

        for test in self.__tests__:
            if not test(self):
                return False

        return True

    def add(self, name):
        if name not in self.__subgroups__:
            self.__subgroups__ = self.__subgroups__ + (name,)

            id = self.__id__
            if id:
                id = id + '.'

            items = []
            for grp_id in self.__subgroups__:
                name = id + grp_id

                group = queryUtility(IPreferenceGroup, name)

                # this code for support z3c.baseregistry package
                if group is None:
                    group = getGlobalSiteManager().queryUtility(
                        IPreferenceGroup, name)

                if group is not None:
                    items.append((group.order, group.__title__, grp_id))

            items.sort()
            self.__subgroups__ = tuple([id for o,t,id in items])

    def remove(self, name):
        if name in self.__subgroups__:
            names = list(self.__subgroups__)
            names.remove(name)
            self.__subgroups__ = tuple(names)

    def get(self, key, default=None):
        id = self.__id__ and self.__id__ + '.' + key or key
        group = queryUtility(IPreferenceGroup, id, default)
        if group is default:
            return default
        return group.__bind__(self.__principal__, self)

    def items(self):
        id = self.__id__
        if id:
            id = id + '.'

        items = []
        for key in self.keys():
            name = id + key
            group = queryUtility(IPreferenceGroup, name)
            if group is not None:
                items.append((name, group.__bind__(self.__principal__, self)))
        return items

    def __getitem__(self, key):
        obj = self.get(key, _marker)
        if obj is _marker:
            raise KeyError(key)
        return obj

    def __contains__(self, key):
        return key in self.keys()

    def keys(self):
        return self.__subgroups__

    def __iter__(self):
        id = self.__id__
        if id:
            id = id + '.'

        for key in self.keys():
            name = id + key
            group = queryUtility(IPreferenceGroup, name)
            if group is not None:
                yield group.__bind__(self.__principal__, self)

    def values(self):
        return [group for id, group in self.items()]

    def __len__(self):
        return len(self.keys())
