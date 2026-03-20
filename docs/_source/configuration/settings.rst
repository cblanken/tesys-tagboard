Settings
========

Environment Variable Overview
-----------------------------

Most settings are defined by environment variables. They may be set in
an ``.env`` file in the project’s root directory to adjust various
aspects of the deployment.

See their usage details below.

General App Settings
~~~~~~~~~~~~~~~~~~~~

These environment variables are read by the Django app and thus have a
corresponding value in Django accessible via ``django.conf.settings``.

=========================================== ==================================== ====================== =======================
Environment Variable                        Django Setting                       Production Default     Development Default
=========================================== ==================================== ====================== =======================
`ACCOUNT_EMAIL_VERIFICATION`_               ``DJANGO_EMAIL_VERIFICATION``        optional               optional
`DATABASE_URL`_                             ``DATABASES["default"]``
`DJANGOADMIN_FORCE_ALLAUTH`_                ``DJANGO_ADMIN_FORCE_ALLAUTH``       False                  False
`DJANGO_ACCOUNT_ALLOW_REGISTRATION`_        ``ACCOUNT_ALLOW_REGISTRATION``       True                   True
`DJANGO_ADMINS`_                            ``ADMINS``                           []                     []
`DJANGO_ADMIN_URL`_                         ``ADMIN_URL``                        ``/admin``
`DJANGO_ALLOWED_HOSTS`_                     ``ALLOWED_HOSTS``
`DJANGO_DEBUG_TOOLBAR`_                     ``DEBUG_TOOLBAR``                    True
`DJANGO_DEBUG`_                             ``DEBUG``                            False                  True
`DJANGO_HOMEPAGE_LINKS`_                    ``HOMEPAGE_LINKS``
`DJANGO_SECURE_CONTENT_TYPE_NOSNIFF`_       ``SECURE_CONTENT_TYPE_NOSNIFF``                             True
`DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`_    ``SECURE_HSTS_INCLUDE_SUBDOMAINS``                          True
`DJANGO_SECURE_HSTS_PRELOAD`_               ``SECURE_HSTS_PRELOAD``                                     True
`DJANGO_SECURE_SSL_REDIRECT`_               ``SECURE_SSL_REDIRECT``                                     True
`DJANGO_SILKY_PYTHON_PROFILER_BINARY`_      ``SILKY_PYTHON_PROFILER_BINARY``     False                  False
`DJANGO_SILKY_PYTHON_PROFILER`_             ``SILKY_PYTHON_PROFILER``            False                  False
`DJANGO_SOCIAL_LOGIN_ENABLED`_              ``SOCIALACCOUNT_ENABLED``            True                   True
`DJANGO_TITLE`_                             ``TITLE``                            Tesy's Tagboard        Tesy's Tagboard
`USE_DOCKER`_                                                                    yes                    yes
=========================================== ==================================== ====================== =======================

Email Settings
~~~~~~~~~~~~~~

================================ ========================= =============================== ================================
Environment Variable             Django Setting            Production Default              Development Default
================================ ========================= =============================== ================================
`DJANGO_DEFAULT_FROM_EMAIL`_     ``DEFAULT_FROM_EMAIL``
`DJANGO_EMAIL_BACKEND`_          ``EMAIL_BACKEND``
`DJANGO_EMAIL_HOST_PASSWORD`_    ``EMAIL_HOST_PASSWORD``                                   tesys_tagboard_local_mailpit
`DJANGO_EMAIL_HOST_USER`_        ``EMAIL_HOST_USER``
`DJANGO_EMAIL_HOST`_             ``EMAIL_HOST``                                            tesys_tagboard_local_mailpit
`DJANGO_EMAIL_PORT`_             ``EMAIL_PORT``                                            1025
`DJANGO_SERVER_EMAIL`_           ``SERVER_EMAIL``          ``DJANGO_DEFAULT_FROM_EMAIL``
================================ ========================= =============================== ================================


Database Settings
~~~~~~~~~~~~~~~~~

======================== ==================
Environment Variable     Default
======================== ==================
`POSTGRES_DB`_           tesys_tagboard
`POSTGRES_PASSWORD`_
`POSTGRES_PORT`_         5432
`POSTGRES_USER`_
======================== ==================


Third-party Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~

================================== ================== ====================== =======================
Environment Variable               Django Setting     Production Default     Development Default
================================== ================== ====================== =======================
`DJANGO_DISCORD_CLIENT_ID`_
`DJANGO_DISCORD_CLIENT_SECRET`_
`DJANGO_DISCORD_PUBLIC_KEY`_
================================== ================== ====================== =======================


Environment Variable Usage
--------------------------
Detailed descriptions of each environment variable and their intended usage.

:code:`ACCOUNT_EMAIL_VERIFICATION`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

====================== ===========================================================
Option
====================== ===========================================================
``optional`` (default) User's *MAY* optionally provide an email at signup which may be used for password resets and other notifications.
``mandatory``          User's *MUST* provide an email
``none``               User's *CANNOT* provide an email. This option usually corresponds with an alternative third-party authentication option. Otherwise user's won't be able to make accounts at all.
====================== ===========================================================


:code:`DATABASE_URL`
~~~~~~~~~~~~~~~~~~~~
By default, the database URL used by the Django application to communicate with the Postgres database
is generated from the `Database Settings`_. This variable will override that generated database URL.

:code:`DJANGOADMIN_FORCE_ALLAUTH`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_ACCOUNT_ALLOW_REGISTRATION`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_ADMINS`
~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_ADMIN_URL`
~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_ALLOWED_HOSTS`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_DEBUG_TOOLBAR`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_DEBUG`
~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_DEFAULT_FROM_EMAIL`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_DISCORD_CLIENT_ID`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_DISCORD_CLIENT_SECRET`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_DISCORD_PUBLIC_KEY`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_EMAIL_BACKEND`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_EMAIL_HOST_PASSWORD`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_EMAIL_HOST_USER`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_EMAIL_HOST`
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_EMAIL_PORT`
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_HOMEPAGE_LINKS`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SECURE_CONTENT_TYPE_NOSNIFF`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SECURE_HSTS_PRELOAD`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SECURE_SSL_REDIRECT`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SERVER_EMAIL`
~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SETTINGS_MODULE`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SILKY_PYTHON_PROFILER_BINARY`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SILKY_PYTHON_PROFILER`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_SOCIAL_LOGIN_ENABLED`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`DJANGO_TITLE`
~~~~~~~~~~~~~~~~~~~~
TODO

:code:`POSTGRES_DB`
~~~~~~~~~~~~~~~~~~~
TODO

:code:`POSTGRES_PASSWORD`
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`POSTGRES_PORT`
~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`POSTGRES_USER`
~~~~~~~~~~~~~~~~~~~~~
TODO

:code:`USE_DOCKER`
~~~~~~~~~~~~~~~~~~
TODO

