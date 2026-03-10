Settings
========

Environment Variable Overview
---------------------

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
`DJANGO_ADMIN_URL`_                         ``ADMIN_URL``                        ``/admin``
`DJANGO_ALLOWED_HOSTS`_                     ``ALLOWED_HOSTS``
`DJANGO_DEBUG_TOOLBAR`_                     ``DEBUG_TOOLBAR``                    True
`DJANGO_DEBUG`_                             ``DEBUG``                            False                  True
`DJANGO_HOMEPAGE_LINKS`_                    ``HOMEPAGE_LINKS``                   ...                    ...
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
`DJANGO_EMAIL_BACKEND`_          ``EMAIL_BACKEND``         ...
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

.. _ACCOUNT_EMAIL_VERIFICATION:

:code:`ACCOUNT_EMAIL_VERIFICATION`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

====================== ===========================================================
Option
====================== ===========================================================
``optional`` (default) User's *MAY* optionally provide an email at signup which may be used for password resets and other notifications.
``mandatory``          User's *MUST* provide an email
``none``               User's *CANNOT* provide an email. This option usually corresponds with an alternative third-party authentication option. Otherwise user's won't be able to make accounts at all.
====================== ===========================================================


.. _DATABASE_URL:

:code:`DATABASE_URL`
~~~~~~~~~~~~~~~~~~~~
By default, the database URL used by the Django application to communicate with the Postgres database
is generated from the `Database Settings`_. This variable will override that generated database URL.

.. _DJANGOADMIN_FORCE_ALLAUTH:

:code:`DJANGOADMIN_FORCE_ALLAUTH`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_ACCOUNT_ALLOW_REGISTRATION:

:code:`DJANGO_ACCOUNT_ALLOW_REGISTRATION`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_ADMIN_URL:

:code:`DJANGO_ADMIN_URL`
~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_ALLOWED_HOSTS:

:code:`DJANGO_ALLOWED_HOSTS`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_DEBUG_TOOLBAR:

:code:`DJANGO_DEBUG_TOOLBAR`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_DEBUG:

:code:`DJANGO_DEBUG`
~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_DEFAULT_FROM_EMAIL:

:code:`DJANGO_DEFAULT_FROM_EMAIL`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_DISCORD_CLIENT_ID:

:code:`DJANGO_DISCORD_CLIENT_ID`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_DISCORD_CLIENT_SECRET:

:code:`DJANGO_DISCORD_CLIENT_SECRET`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_DISCORD_PUBLIC_KEY:

:code:`DJANGO_DISCORD_PUBLIC_KEY`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_EMAIL_BACKEND:

:code:`DJANGO_EMAIL_BACKEND`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_EMAIL_HOST_PASSWORD:

:code:`DJANGO_EMAIL_HOST_PASSWORD`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_EMAIL_HOST_USER:

:code:`DJANGO_EMAIL_HOST_USER`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_EMAIL_HOST:

:code:`DJANGO_EMAIL_HOST`
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_EMAIL_PORT:

:code:`DJANGO_EMAIL_PORT`
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_HOMEPAGE_LINKS:

:code:`DJANGO_HOMEPAGE_LINKS`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SECURE_CONTENT_TYPE_NOSNIFF:

:code:`DJANGO_SECURE_CONTENT_TYPE_NOSNIFF`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS:

:code:`DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SECURE_HSTS_PRELOAD:

:code:`DJANGO_SECURE_HSTS_PRELOAD`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SECURE_SSL_REDIRECT:

:code:`DJANGO_SECURE_SSL_REDIRECT`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SERVER_EMAIL:

:code:`DJANGO_SERVER_EMAIL`
~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SETTINGS_MODULE:

:code:`DJANGO_SETTINGS_MODULE`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SILKY_PYTHON_PROFILER_BINARY:

:code:`DJANGO_SILKY_PYTHON_PROFILER_BINARY`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SILKY_PYTHON_PROFILER:

:code:`DJANGO_SILKY_PYTHON_PROFILER`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_SOCIAL_LOGIN_ENABLED:

:code:`DJANGO_SOCIAL_LOGIN_ENABLED`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _DJANGO_TITLE:

:code:`DJANGO_TITLE`
~~~~~~~~~~~~~~~~~~~~
TODO

.. _POSTGRES_DB:

:code:`POSTGRES_DB`
~~~~~~~~~~~~~~~~~~~
TODO

.. _POSTGRES_PASSWORD:

:code:`POSTGRES_PASSWORD`
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

.. _POSTGRES_PORT:

:code:`POSTGRES_PORT`
~~~~~~~~~~~~~~~~~~~~~
TODO

.. _POSTGRES_USER:

:code:`POSTGRES_USER`
~~~~~~~~~~~~~~~~~~~~~
TODO

.. _USE_DOCKER:

:code:`USE_DOCKER`
~~~~~~~~~~~~~~~~~~
TODO


