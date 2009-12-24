================
User Preferences
================

Implementing user preferences is usually a painful task, since it requires a
lot of custom coding and constantly changing preferences makes it hard to
maintain the data and UI. The `preference` package

  >>> from zojax.preferences import interfaces, preference, preferencetype

eases this pain by providing a generic user preferences framework that uses
schemas to categorize and describe the preferences.

We also have to do some additional setup beforehand:

  >>> from zope.app.testing import setup

  >>> import zope.app.component.hooks
  >>> zope.app.component.hooks.setHooks()
  >>> setup.setUpTraversal()
  >>> setup.setUpSiteManagerLookup()


Preference Groups
------------------

Preferences are grouped in preference groups and the preferences inside a
group are specified via the preferences group schema:

  >>> import zope.schema
  >>> import zope.interface

  >>> class IZMIUserSettings(zope.interface.Interface):
  ...     """Basic User Preferences"""
  ...
  ...     email = zope.schema.TextLine(
  ...         title=u"E-mail Address",
  ...         description=u"E-mail Address used to send notifications")
  ...
  ...     skin = zope.schema.Choice(
  ...         title=u"Skin",
  ...         description=u"The skin that should be used for the ZMI.",
  ...         values=['Rotterdam', 'ZopeTop', 'Basic'],
  ...         default='Rotterdam')
  ...
  ...     showZopeLogo = zope.schema.Bool(
  ...         title=u"Show Zope Logo",
  ...         description=u"Specifies whether Zope logo should be displayed "
  ...                     u"at the top of the screen.",
  ...         default=True)

Each preference group must have an
ID by which it can be accessed and optional title and description fields for UI
purposes. Before create preference group we should create unique class for
our preferences:

  >>> settingsClass = preferencetype.PreferenceType(
  ...     "ZMISettings",
  ...     IZMIUserSettings,
  ...     title=u"ZMI User Settings", description=u"")

We should set 'preferenceID' to schema with preference group id,
This value is used by data storage to store data in annotations

  >>> IZMIUserSettings.setTaggedValue('preferenceID', 'ZMISettings')

Now we can instantiate the preference group.

  >>> settings = settingsClass()

We can't change schema for preference group:

  >>> settings.__schema__ = IZMIUserSettings
  Traceback (most recent call last):
  ...
  AttributeError: Can't change __schema__


Note that the preferences group provides the interface it is representing:

  >>> IZMIUserSettings.providedBy(settings)
  True

and the id, schema and title of the group are directly available:

  >>> settings.__id__
  u'ZMISettings'
  >>> settings.__schema__
  <InterfaceClass zojax.preferences.README.IZMIUserSettings>
  >>> settings.__title__
  u'ZMI User Settings'

So let's ask the preference group for the `skin` setting:

  >>> settings.skin
  Traceback (most recent call last):
  ...
  UnboundPreferenceGroup


So why did the lookup fail? Because we have not specified a principal yet, for
which we want to lookup the preferences. To do that, we have to create a principal:

  >>> class Principal:
  ...     def __init__(self, id):
  ...         self.id = id
  >>> principal = Principal('zope.user')

  >>> class Participation:
  ...     interaction = None
  ...     def __init__(self, principal):
  ...         self.principal = principal

  >>> participation = Participation(principal)

  >>> import zope.security.management
  >>> zope.security.management.newInteraction(participation)

We also need an IAnnotations adapter for principals, so we can store the
settings:

  >>> from zope.annotation.interfaces import IAnnotations
  >>> class PrincipalAnnotations(dict):
  ...     zope.interface.implements(IAnnotations)
  ...     data = {}
  ...     def __new__(class_, principal):
  ...         try:
  ...             annotations = class_.data[principal.id]
  ...         except KeyError:
  ...             annotations = dict.__new__(class_)
  ...             class_.data[principal.id] = annotations
  ...         return annotations
  ...     def __init__(self, principal):
  ...         pass

  >>> from zope import component
  >>> component.provideAdapter(PrincipalAnnotations, (Principal,), IAnnotations)

Also we need IDataStorage for preferenceGroup schema, because preference group
doesn't use IAnnotations directly.

  >>> from zojax.preferences import storage
  >>> component.provideAdapter(
  ...     storage.getDefaultStorage, (Principal, zope.interface.Interface))

And now we need bind preferences to principal. We can just call __bind__
method in this case preference will use principal from current interaction.

  >>> nsettings = settings.__bind__()
  >>> interfaces.IBound.providedBy(nsettings)
  True

  >>> nsettings.__principal__ == principal
  True

Or we can explicitly set principal, this is usefull when we want to know
preferences for principal.

  >>> settings = settings.__bind__(principal)
  >>> interfaces.IBound.providedBy(nsettings)
  True

Let's now try to access the settings again:

  >>> settings.skin
  'Rotterdam'

which is the default value, since we have not set it yet. We can now reassign
the value:

  >>> settings.skin = 'Basic'
  >>> settings.skin
  'Basic'

However, you cannot just enter any value, since it is validated before the
assignment:

  >>> settings.skin = 'MySkin'
  Traceback (most recent call last):
  ...
  ConstraintNotSatisfied: MySkin


Preference Group Trees
----------------------

The preferences would not be very powerful, if you could create a full
preferences. So let's create a sub-group for our ZMI user settings, where we
can adjust the look and feel of the folder contents view:

  >>> class IFolderSettings(zope.interface.Interface):
  ...     """Basic User Preferences"""
  ...
  ...     shownFields = zope.schema.Tuple(
  ...         title=u"Shown Fields",
  ...         description=u"Fields shown in the table.",
  ...         value_type=zope.schema.Choice(['name', 'size', 'creator']),
  ...         default=('name', 'size'))
  ...
  ...     sortedBy = zope.schema.Choice(
  ...         title=u"Sorted By",
  ...         description=u"Data field to sort by.",
  ...         values=['name', 'size', 'creator'],
  ...         default='name')

  >>> folderSettingsClass = preferencetype.PreferenceType(
  ...     "ZMISettings.Folder",
  ...     IFolderSettings,
  ...     title=u"Folder Content View Settings")

  >>> IFolderSettings.setTaggedValue('preferenceID', 'ZMISettings.Folder')

  >>> folderSettings = folderSettingsClass()

Note that the id was chosen so that the parent id is the prefix of the child's
id. Our new preference sub-group should now be available as an attribute or an
item on the parent group ...

  >>> settings['Folder']
  Traceback (most recent call last):
  ...
  KeyError: 'Folder'

but not before we register the groups as utilities:

  >>> from zope import component
  >>> siteManager = component.getSiteManager()

  >>> siteManager.registerUtility(
  ...     settings, interfaces.IPreferenceGroup, 'ZMISettings')
  >>> siteManager.registerUtility(
  ...     folderSettings, interfaces.IPreferenceGroup, 'ZMISettings.Folder')

If we now try to lookup the sub-group again, we should be successful:

  >>> settings['Folder']
  <zojax.preferences.preferencetype.Preference<ZMISettings.Folder> ...>

In zojax.preferences we can't access to subfolder as attribute, this
is one of difference from zope.app.preference.

  >>> settings['Folder'].sortedBy = 'size'
  >>> settings['Folder'].sortedBy
  'size'

While the registry of the preference groups is flat, the careful naming of the
ids allows us to have a tree of preferences. Note that this pattern is very
similar to the way modules are handled in Python; they are stored in a flat
dictionary in ``sys.modules``, but due to the naming they appear to be in a
namespace tree.

While we are at it, there are also preference categories that can be compared
to Python packages. They basically are just a higher level grouping concept
that is used by the UI to better organize the preferences. A preference group
can be converted to a category by simply providing an additional interface:

  >>> zope.interface.alsoProvides(settings, interfaces.IPreferenceCategory)

  >>> interfaces.IPreferenceCategory.providedBy(settings)
  True

Clear:

  >>> t = siteManager.unregisterUtility(
  ...     settings, interfaces.IPreferenceGroup, 'ZMISettings')
  >>> t = siteManager.unregisterUtility(
  ...     folderSettings, interfaces.IPreferenceGroup, 'ZMISettings.Folder')


Creating Preference Groups Using ZCML
-------------------------------------

If you are using the user preference system in Zope 3, you will not have to
manually setup the preference groups as we did above (of course). We will use
ZCML instead. First, we need to register the directives:

  >>> from zope.configuration import xmlconfig
  >>> import zojax.preferences
  >>> context = xmlconfig.file('meta.zcml', zojax.preferences)

Second we need root preference group:

  >>> from zojax.preferences.root import PersonalPreferences

  >>> siteManager.registerUtility(
  ...     PersonalPreferences(), interfaces.IPreferenceGroup)

Then the system sets up a root preference group:

  >>> context = xmlconfig.string('''
  ... <configure
  ...    xmlns:zojax="http://namespaces.zope.org/zojax" i18n_domain="test">
  ... 
  ...   <zojax:preferenceGroup
  ...     id="ZMISettings"
  ...     schema="zojax.preferences.README.IZMIUserSettings"
  ...     title="ZMI User Settings"
  ...     permission="zope.Public" />
  ...
  ...   <zojax:preferenceGroup
  ...     id="ZMISettings.Folder"
  ...     schema="zojax.preferences.README.IFolderSettings"
  ...     title="Folder Content View Settings"
  ...     permission="zope.Public" />
  ...
  ... </configure>''', context)

Now we can use the preference system in its intended way. We access the folder
settings as follows:

  >>> prefs = component.getUtility(interfaces.IPreferenceGroup)
  >>> prefs.isAvailable()
  False

  >>> prefs['ZMISettings']['Folder'].isAvailable()
  False


Don't forget to bind preferences to principal

  >>> prefs = prefs.__bind__(principal)
  >>> prefs.isAvailable()
  True

  >>> p = prefs['ZMISettings']['Folder'].__bind__(parent=prefs)

  >>> prefs['ZMISettings']['Folder'].isAvailable()
  True

  >>> prefs['ZMISettings']['Folder'].sortedBy
  'size'

  >>> prefs.items()
  [(u'ZMISettings', <zojax.preferences.preferencetype.Preference<ZMISettings> ...>)]

  >>> u'ZMISettings' in prefs
  True

  >>> prefs.keys()
  (u'ZMISettings',)

  >>> prefs.values()
  [<zojax.preferences.preferencetype.Preference<ZMISettings> ...>]

  >>> list(iter(prefs))
  [<zojax.preferences.preferencetype.Preference<ZMISettings> ...>]

  >>> len(prefs)
  1


Let's register the ZMI settings again under a new name via ZCML:

  >>> class IZMIUserSettings2(IZMIUserSettings):
  ...     pass

  >>> IZMIUserSettings2.setTaggedValue('preferenceID', 'ZMISettings.Folder')

  >>> context = xmlconfig.string('''
  ... <configure
  ...   xmlns:zojax="http://namespaces.zope.org/zojax"
  ...   i18n_domain="test">
  ...
  ...   <zojax:preferenceGroup
  ...      id="ZMISettings2"
  ...      title="ZMI Settings NG"
  ...      schema="zojax.preferences.README.IZMIUserSettings"
  ...      permission="zope.Public"
  ...      provides="zojax.preferences.interfaces.IPreferenceCategory" />
  ...
  ...     </configure>''', context)

  >>> prefs['ZMISettings2']
  <zojax.preferences.preferencetype.Preference<ZMISettings2> ...>

  >>> prefs['ZMISettings2'].__title__
  u'ZMI Settings NG'

  >>> IZMIUserSettings.providedBy(prefs['ZMISettings2'])
  True
  >>> interfaces.IPreferenceCategory.providedBy(prefs['ZMISettings2'])
  True

And the tree can built again by carefully constructing the id:

  >>> context = xmlconfig.string('''
  ... <configure
  ...   xmlns:zojax="http://namespaces.zope.org/zojax"
  ...   i18n_domain="test">
  ...
  ...   <zojax:preferenceGroup
  ...     id="ZMISettings2.Folder"
  ...     title="Folder Settings"
  ...     schema="zojax.preferences.README.IFolderSettings" />
  ...
  ...     </configure>''', context)

  >>> prefs['ZMISettings2']
  <zojax.preferences.preferencetype.Preference<ZMISettings2> ...>

  >>> prefs['ZMISettings2'].items()
  [(u'ZMISettings2.Folder', <zojax.preferences.preferencetype.Preference<ZMISettings2.Folder> ...)]

  >>> list(iter(prefs['ZMISettings2']))
  [<zojax.preferences.preferencetype.Preference<ZMISettings2.Folder> ...>]

  >>> prefs['ZMISettings2']['Folder'].__title__
  u'Folder Settings'

  >>> IFolderSettings.providedBy(prefs['ZMISettings2']['Folder'])
  True
  >>> interfaces.IPreferenceCategory.providedBy(prefs['ZMISettings2']['Folder'])
  False

We can define preference group for principal type

  >>> class IMyPrincipal(zope.interface.Interface):
  ...   pass

Now let's register preference for for this type of principal

  >>> context = xmlconfig.string('''
  ... <configure
  ...   xmlns:zojax="http://namespaces.zope.org/zojax"
  ...   i18n_domain="test">
  ...
  ...   <zojax:preferenceGroup
  ...     id="ZMISettings2.Folder10"
  ...     for="zojax.preferences.README.IMyPrincipal"
  ...     title="Folder Settings"
  ...     permission="zope.Public"
  ...     schema="zojax.preferences.README.IFolderSettings" />
  ...
  ...     </configure>''', context)

  >>> p = component.getUtility(interfaces.IPreferenceGroup, 'ZMISettings2.Folder10')
  >>> new_prefs = p.__bind__()
  >>> new_prefs.isAvailable()
  False

Now let's mark our principal

  >>> zope.interface.alsoProvides(principal, IMyPrincipal)
  >>> new_prefs = p.__bind__()
  >>> new_prefs.isAvailable()
  True

  >>> prefs['ZMISettings2'].remove('Folder10')


Simple Python-Level Access
--------------------------

If a site is set, getting the user preferences is very simple:

  >>> prefs2 = IFolderSettings(principal)

  >>> prefs2.sortedBy
  'name'


Security
--------

You might already wonder under which permissions the preferences are
available. They are actually available with zojax.ManagePreference
permission. But sometimes we need preferences which can be changed
only by manager. In this case we can provide default permission or
even set security checks on attribute level, like in <class /> directive.

  >>> import zope.security
  >>> context = xmlconfig.file('meta.zcml', zope.security, context)

  >>> context = xmlconfig.string('''
  ... <configure
  ...   xmlns="http://namespaces.zope.org/zope"
  ...   xmlns:zojax="http://namespaces.zope.org/zojax"
  ...   i18n_domain="zojax">
  ... 
  ...   <permission id="zope.View" title="zope view" />
  ...   <permission id="zope.Manage" title="zope manage" />
  ... 
  ...   <zojax:preferenceGroup
  ...      id="ZMISettings3"
  ...      title="ZMI Settings 3"
  ...      schema="zojax.preferences.README.IZMIUserSettings"
  ...      provides="zojax.preferences.interfaces.IPreferenceCategory"
  ...      permission="zope.View">
  ...    <allow attributes="email" />
  ...    <require
  ...      attributes="showZopeLogo" permission="zope.Manage" set_attributes="skin" />
  ...   </zojax:preferenceGroup>
  ...
  ... </configure>''', context)

