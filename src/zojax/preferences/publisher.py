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
from zope.publisher.interfaces import NotFound
from z3c.traverser.interfaces import ITraverserPlugin


class PreferenceTraverserPlugin(object):
    """A traverser that knows how to look up objects by name in a container."""
    interface.implements(ITraverserPlugin)

    def __init__(self, container, request):
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        try:
            subob = self.context.get(name, None)
        except:
            subob = None

        if subob is None:
            raise NotFound(self.context, name, request)

        return subob
