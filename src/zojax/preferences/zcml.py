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
""" zojax:preferenceGroup directive implementation

$Id$
"""
from zope import interface
from zope.schema import Int
from zope.component import getUtility, queryUtility, getGlobalSiteManager
from zope.schema.interfaces import IField
from zope.location.interfaces import ILocation

from zope.security.zcml import Permission
from zope.security.checker import Checker, CheckerPublic
from zope.security.interfaces import IPrincipal

from zope.interface.common.mapping import IEnumerableMapping

from zope.component.zcml import utility, adapter
from zope.component.interface import provideInterface

from zope.configuration import fields
from zope.configuration.exceptions import ConfigurationError

from zope.app.security.protectclass import \
    protectName, protectSetAttribute, protectLikeUnto

from preference import PreferenceGroup
from interfaces import IPreferenceGroup
from preferencetype import PreferenceType
from utils import PrincipalChecker, PermissionChecker


class IPreferenceGroupDirective(interface.Interface):
    """Register a preference group."""

    id = fields.PythonIdentifier(
        title=u"Id",
        description=u"""
            Id of the preference group used to access the group. The id should
            be a valid path in the preferences tree.""",
        required=True)

    for_ = fields.GlobalInterface(
        title=u"For",
        description=u"Principal interface to use this preference for.",
        required=False)

    schema = fields.GlobalInterface(
        title=u"Schema",
        description=u"Schema of the preference group used defining the "
                    u"preferences of the group.",
        required=True)

    title = fields.MessageID(
        title=u"Title",
        description=u"Title of the preference group used in UIs.",
        required=True)

    description = fields.MessageID(
        title=u"Description",
        description=u"Description of the preference group used in UIs.",
        required=False)

    class_ = fields.GlobalObject(
        title=u"Class",
        description=u"Custom IPreferenceGroup implementation.",
        required=False)

    provides = fields.Tokens(
        title = u'Provides',
        required = False,
        value_type = fields.GlobalInterface())

    permission = Permission(
        title = u'Permission',
        description = u'Default set schema permission.',
        required = False)

    accesspermission = Permission(
        title = u'Access permission',
        description = u'Default access permission.',
        required = False)

    tests = fields.Tokens(
        title = u"Tests",
        description = u'Tests for check availability.',
        value_type = fields.GlobalObject(),
        required = False)

    order = Int(
        title = u'Order',
        default = 999999,
        required = False)


class PreferenceGroupAdapter(object):

    def __init__(self, name):
        self.name = name

    def __call__(self, principal, context=None):
        prefs = getUtility(IPreferenceGroup, self.name)
        return prefs.__bind__(principal, context)


class PreferenceGroupDirective(object):

    def __init__(self, _context, id, schema, title,
                 for_=None, description=u'', class_=None, provides=[],
                 permission='zojax.ModifyPreference', accesspermission='',
                 tests=(), order = 9999):

        if not accesspermission:
            accesspermission = permission

        if permission == 'zope.Public':
            permission = CheckerPublic

        if accesspermission == 'zope.Public':
            accesspermission = CheckerPublic

        Class = PreferenceType(str(id), schema, class_, title, description)
        Class.order = order
        Class.__permission__ = permission
        Class.__accesspermission__ = accesspermission

        tests = tuple(tests)
        if permission != CheckerPublic:
            tests = tests + (PermissionChecker,)
        if interface.interfaces.IInterface.providedBy(for_):
            tests = tests + (PrincipalChecker(for_),)

        group = Class(tests)

        utility(_context, IPreferenceGroup, group, name=id)
        adapter(_context, (PreferenceGroupAdapter(id),), schema,
                (for_ or IPrincipal,))
        adapter(_context, (PreferenceGroupAdapter(id),), schema,
                (for_ or IPrincipal, interface.Interface))

        interface.classImplements(Class, *provides)

        self._class = Class
        self._context = _context
        self._permission = permission

        self.require(_context, permission, set_schema=(schema,))
        self.require(_context, accesspermission,
                     interface=(IPreferenceGroup, schema))

        self.require(_context, CheckerPublic,
                     interface=(IEnumerableMapping, ILocation),
                     attributes=('isAvailable',
                                 '__id__', '__schema__',
                                 '__title__', '__description__',
                                 '__permission__'))

        schema.setTaggedValue('preferenceID', id)

        _context.action(
            discriminator=('zojax:preferences', schema),
            callable=addSubgroup, args=(group,))

    def require(self, _context,
                permission=None, attributes=None, interface=None,
                set_attributes=None, set_schema=None):
        """Require a permission to access a specific aspect"""
        if not (interface or attributes or set_attributes or set_schema):
            raise ConfigurationError("Nothing required")

        if not permission:
            raise ConfigurationError("No permission specified")

        if interface:
            for i in interface:
                if i:
                    self.__protectByInterface(i, permission)

        if attributes:
            self.__protectNames(attributes, permission)

        if set_attributes:
            self.__protectSetAttributes(set_attributes, permission)

        if set_schema:
            for s in set_schema:
                self.__protectSetSchema(s, permission)

    def allow(self, _context, attributes=None, interface=None):
        """Like require, but with permission_id zope.Public"""
        return self.require(_context, self._permission, attributes, interface)

    def __protectByInterface(self, interface, permission_id):
        "Set a permission on names in an interface."
        for n, d in interface.namesAndDescriptions(1):
            self.__protectName(n, permission_id)

        self._context.action(
            discriminator = None,
            callable = provideInterface,
            args = (interface.__module__+'.'+interface.getName(), interface))

    def __protectName(self, name, permission_id):
        "Set a permission on a particular name."
        self._context.action(
            discriminator = ('zojax:preferences:protectName', object()),
            callable = protectName,
            args = (self._class, name, permission_id))

    def __protectNames(self, names, permission_id):
        "Set a permission on a bunch of names."
        for name in names:
            self.__protectName(name, permission_id)

    def __protectSetAttributes(self, names, permission_id):
        "Set a permission on a bunch of names."
        for name in names:
            self._context.action(
                discriminator = (
                    'zojax:preferences:protectSetAttribute', object()),
                callable = protectSetAttribute,
                args = (self._class, name, permission_id))

    def __protectSetSchema(self, schema, permission_id):
        "Set a permission on a bunch of names."
        _context = self._context

        for name in schema:
            field = schema[name]
            if IField.providedBy(field) and not field.readonly:
                _context.action(
                    discriminator = (
                        'zojax:preferences:protectSetAttribute', object()),
                    callable = protectSetAttribute,
                    args = (self._class, name, permission_id))

        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (schema.__module__+'.'+schema.getName(), schema))


def addSubgroup(group):
    if '.' in group.__id__:
        parentId = group.__id__.split('.')[0]
    else:
        parentId = ''

    parent = queryUtility(IPreferenceGroup, parentId)
    if parent is None:
        parent = getGlobalSiteManager().getUtility(IPreferenceGroup, parentId)

    parent.add(group.__name__)
    group.__parent__ = parent
