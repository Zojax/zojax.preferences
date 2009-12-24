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
""" zojax.preferences interfaces

$Id$
"""
from zope import schema, interface
from zope.configuration import fields
from zope.location.interfaces import ILocation
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zojax.preferences')

ANNOTATION_KEY = 'zope.app.user.UserPreferences'


class UnboundPreferenceGroup(Exception):
    """ Prefernce group is not bound to principal """


class IPreferenceGroup(ILocation):
    """A group of preferences.

    This component represents a logical group of preferences. The preferences
    contained by this group is defined through the schema. The group has also
    a name by which it can be accessed.

    The fields specified in the schema *must* be available as attributes and
    items of the group instance. It is up to the implementation how this is
    realized, however, most often one will implement __setattr__ and
    __getattr__ as well as the common mapping API.

    The reason all the API fields are doubly underlined is to avoid name clashes.
    """

    __id__ = schema.TextLine(
        title = u"Id",
        description = u"The id of the group.",
        required = True)

    __schema__ = schema.InterfaceField(
        title = u"Schema",
        description = u"Schema describing the preferences of the group.",
        required = False,
        readonly = True)

    __title__ = fields.MessageID(
        title = u"Title",
        description = u"The title of the group used in the UI.",
        required = True)

    __description__ = fields.MessageID(
        title = u"Description",
        description = u"The description of the group used in the UI.",
        required = False)

    __principal__ = interface.Attribute('Owner principal of preferences')
    __permission__ = interface.Attribute('Set schema permission')
    __accesspermission__ = interface.Attribute('Access schema permission')

    def isAvailable():
        """ is group available for bound principal """

    def add(name):
        """ add subgroup name """

    def remove(name):
        """ remove subgroup name """

    def __bind__(principal=None, parent=None):
        """ bind preferences """


class IPreferenceCategory(interface.Interface):
    """A collection of preference groups.

    Objects providing this interface serve as groups of preference
    groups. This allows UIs to distinguish between high- and low-level
    prefernce groups.
    """


class IBound(interface.Interface):
    """ bound to context """

    __principal__ = interface.Attribute('IPrincipal object')


class IRootPreferences(interface.Interface):
    """ root preferences """

    def __bind__(principal=None, parent=None):
        """ bind preferences """


class IDataStorage(interface.Interface):
    """ data storage, set/get values as attributes """


class IPortalPreferences(IPreferenceCategory):
    """ portal preferences """


class IMembershipPreferences(IPreferenceCategory):
    """ membership principal preferences """
