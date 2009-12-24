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
""" PreferenceGroup metaclass

$Id$
"""
import sys
from zope import interface
from zope.schema import getFields
from zojax.preferences.interfaces import _
from zojax.preferences.preference import PreferenceGroup

_marker = object()


class PreferenceType(type):
    """ Metaclass for all preference groups

    >>> from zope import interface, schema
    >>> from zojax.preferences import preferencetype

    >>> class IMyPreference(interface.Interface):
    ...   title = schema.TextLine(title = u'Title')

    >>> class MyPreference(object):
    ...   pass

    >>> PreferenceClass = preferencetype.PreferenceType(
    ...    'mypreference', IMyPreference, MyPreference, 'MyPreference', '')

    New class avilable by it's cname in zojax.preferences.preferencetype module

    >>> getattr(preferencetype, 'Preference<mypreference>') is PreferenceClass
    True

    Automaticly generate schema fields to PreferenceProperty

    >>> PreferenceClass.title
    <zojax.preferences.preferencetype.PreferenceProperty object at ...>

    >>> preference = PreferenceClass()
    >>> preference
    <zojax.preferences.preferencetype.Preference<mypreference> object at ...>

    >>> isinstance(preference, MyPreference)
    True

    >>> isinstance(preference, preferencetype.PreferenceGroup)
    True

    We also can use number of base classes

    >>> class MyPreference2(object):
    ...   pass

    >>> PreferenceClass = preferencetype.PreferenceType(
    ...    'mypreference', IMyPreference,
    ...    (MyPreference, MyPreference2), 'MyPreference', '')

    """

    def __new__(cls, name, schema, class_=None, *args, **kw):
        cname = 'Preference<%s>'%name
        if type(class_) is tuple:
            bases = class_ + (PreferenceGroup,)
        elif class_ is not None:
            bases = (class_, PreferenceGroup)
        else:
            bases = (PreferenceGroup,)

        tp = type.__new__(cls, str(cname), bases, {})
        setattr(sys.modules['zojax.preferences.preferencetype'], cname, tp)

        return tp

    def __init__(cls, name, schema, class_=None, title='', description=''):
        for f_id in getFields(schema):
            if not hasattr(cls, f_id):
                setattr(cls, f_id, PreferenceProperty(schema[f_id]))

        cls.__id__ = unicode(name)
        cls.__title__ = title
        cls.__description__ = description
        cls.__schema__ = DataProperty(schema)
        interface.classImplements(cls, schema)


class DataProperty(object):

    def __init__(self, schema):
        self.schema = schema

    def __get__(self, inst, klass):
        return self.schema

    def __set__(self, inst, value):
        raise AttributeError("Can't change __schema__")


class PreferenceProperty(object):
    """ Special property thats reads and writes values from
    instance's 'data' attribute

    Let's define simple schema field

    >>> from zope import schema
    >>> field = schema.TextLine(
    ...    title = u'Test',
    ...    default = u'default value')
    >>> field.__name__ = 'attr1'

    >>> from zojax.preferences.storage import DataStorage

    Now we need content class

    >>> from zojax.preferences.preferencetype import PreferenceProperty
    >>> class Content(object):
    ...
    ...    attr1 = PreferenceProperty(field)

    Lets create class instance and add field values storage

    >>> ob = Content()
    >>> ob.data = DataStorage({}, None)

    By default we should get field default value

    >>> ob.attr1
    u'default value'

    We can set only valid value

    >>> ob.attr1 = 'value1'
    Traceback (most recent call last):
    ...
    WrongType: ('value1', <type 'unicode'>)

    >>> ob.attr1 = u'value1'
    >>> ob.attr1
    u'value1'

    If storage contains field value we shuld get it

    >>> ob.data.attr1 = u'value2'
    >>> ob.attr1
    u'value2'

    We can't set value for readonly fields

    >>> field.readonly = True
    >>> ob.attr1 = u'value1'
    Traceback (most recent call last):
    ...
    ValueError: ('attr1', u'Field is readonly')

    Remove attribute

    >>> del ob.attr1

    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self._field = field
        self._name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = getattr(inst.data, self._name, _marker)
        if value is _marker:
            return self._field.default

        return value

    def __set__(self, inst, value):
        field = self._field.bind(inst)
        field.validate(value)
        if field.readonly and hasattr(inst.data, self._name):
            raise ValueError(self._name, _(u'Field is readonly'))
        setattr(inst.data, self._name, value)

    def __delete__(self, inst):
        if hasattr(inst.data, self._name):
            delattr(inst.data, self._name)
