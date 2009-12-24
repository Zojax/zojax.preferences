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
"""Tests for the Preferences System

$Id$
"""
import os.path, unittest, doctest

from zope import component
from zope.component import testing
from zope.testing import doctestunit
from zope.app.testing import setup, functional

from zope.app.rotterdam import Rotterdam
from zope.app.principalannotation import PrincipalAnnotationUtility
from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility
from zojax.layoutform.interfaces import ILayoutFormLayer


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


zojaxPreferences = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxPreferences', allow_teardown=True)


def FunctionalDocFileSuite(*paths, **kw):
    globs = kw.setdefault('globs', {})
    globs['sync'] = functional.sync
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        root = functional.getRootFolder()
        root['principalannotation'] = PrincipalAnnotationUtility()
        root.getSiteManager().registerUtility(
            root['principalannotation'], IPrincipalAnnotationUtility)

    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        functional.FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = zojaxPreferences
    return suite


def setUp(test):
    testing.setUp(test)
    setup.setUpTestAsModule(test, 'zojax.preferences.README')

def tearDown(test):
    testing.tearDown(test)
    setup.tearDownTestAsModule(test)

def notAvailable(*args):
    return None

def test_suite():
    testbrowser = FunctionalDocFileSuite("testbrowser.txt")

    return unittest.TestSuite((
            testbrowser,
            doctest.DocFileSuite(
                '../README.txt',
                setUp=setUp, tearDown=tearDown,
                globs={'pprint': doctestunit.pprint},
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'zojax.preferences.utils',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'zojax.preferences.preferencetype',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
