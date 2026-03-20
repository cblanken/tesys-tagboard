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

================================================== ==================================== ====================== =======================
Environment Variable                               Django Setting                       Production Default     Development Default
================================================== ==================================== ====================== =======================
:envvar:`ACCOUNT_EMAIL_VERIFICATION`               ``DJANGO_EMAIL_VERIFICATION``        ``optional``           ``optional``
:envvar:`DATABASE_URL`                             ``DATABASES["default"]``
:envvar:`DJANGOADMIN_FORCE_ALLAUTH`                ``DJANGO_ADMIN_FORCE_ALLAUTH``       ``False``              ``False``
:envvar:`DJANGO_ACCOUNT_ALLOW_REGISTRATION`        ``ACCOUNT_ALLOW_REGISTRATION``       ``True``               ``True``
:envvar:`DJANGO_ADMINS`                            ``ADMINS``                           ``[]``                 ``[]``
:envvar:`DJANGO_ADMIN_URL`                         ``ADMIN_URL``                        ``/admin``
:envvar:`DJANGO_ALLOWED_HOSTS`                     ``ALLOWED_HOSTS``
:envvar:`DJANGO_DEBUG_TOOLBAR`                     ``DEBUG_TOOLBAR``                    ``True``
:envvar:`DJANGO_DEBUG`                             ``DEBUG``                            ``False``              ``True``
:envvar:`DJANGO_HOMEPAGE_LINKS`                    ``HOMEPAGE_LINKS``
:envvar:`DJANGO_SECURE_CONTENT_TYPE_NOSNIFF`       ``SECURE_CONTENT_TYPE_NOSNIFF``                             ``True``
:envvar:`DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`    ``SECURE_HSTS_INCLUDE_SUBDOMAINS``                          ``True``
:envvar:`DJANGO_SECURE_HSTS_PRELOAD`               ``SECURE_HSTS_PRELOAD``                                     ``True``
:envvar:`DJANGO_SECURE_SSL_REDIRECT`               ``SECURE_SSL_REDIRECT``                                     ``True``
:envvar:`DJANGO_SILKY_PYTHON_PROFILER_BINARY`      ``SILKY_PYTHON_PROFILER_BINARY``     ``False``              ``False``
:envvar:`DJANGO_SILKY_PYTHON_PROFILER`             ``SILKY_PYTHON_PROFILER``            ``False``              ``False``
:envvar:`DJANGO_SOCIAL_LOGIN_ENABLED`              ``SOCIALACCOUNT_ENABLED``            ``True``               ``True``
:envvar:`DJANGO_TITLE`                             ``TITLE``                            ``Tesy's Tagboard``    ``Tesy's Tagboard``
:envvar:`USE_DOCKER`                                                                    ``yes``                ``yes``
================================================== ==================================== ====================== =======================

Email Settings
~~~~~~~~~~~~~~

======================================= ========================= =============================== ================================
Environment Variable                    Django Setting            Production Default              Development Default
======================================= ========================= =============================== ================================
:envvar:`DJANGO_DEFAULT_FROM_EMAIL`     ``DEFAULT_FROM_EMAIL``
:envvar:`DJANGO_EMAIL_BACKEND`          ``EMAIL_BACKEND``
:envvar:`DJANGO_EMAIL_HOST_PASSWORD`    ``EMAIL_HOST_PASSWORD``                                   ``tesys_tagboard_local_mailpit``
:envvar:`DJANGO_EMAIL_HOST_USER`        ``EMAIL_HOST_USER``
:envvar:`DJANGO_EMAIL_HOST`             ``EMAIL_HOST``                                            ``tesys_tagboard_local_mailpit``
:envvar:`DJANGO_EMAIL_PORT`             ``EMAIL_PORT``                                            ``1025``
:envvar:`DJANGO_SERVER_EMAIL`           ``SERVER_EMAIL``          ``DJANGO_DEFAULT_FROM_EMAIL``
======================================= ========================= =============================== ================================


Database Settings
~~~~~~~~~~~~~~~~~

=========================== ==================
Environment Variable        Default
=========================== ==================
:envvar:`POSTGRES_DB`       ``tesys_tagboard``
:envvar:`POSTGRES_PASSWORD`
:envvar:`POSTGRES_PORT`     ``5432``
:envvar:`POSTGRES_USER`
=========================== ==================


Third-party Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~

======================================= ================== ====================== =======================
Environment Variable                    Django Setting     Production Default     Development Default
======================================= ================== ====================== =======================
:envvar:`DJANGO_DISCORD_CLIENT_ID`
:envvar:`DJANGO_DISCORD_CLIENT_SECRET`
:envvar:`DJANGO_DISCORD_PUBLIC_KEY`
======================================= ================== ====================== =======================


Environment Variable Usage
--------------------------
Detailed descriptions of each environment variable and their intended usage.

.. envvar:: ACCOUNT_EMAIL_VERIFICATION

====================== ===========================================================
Options
====================== ===========================================================
``optional`` (default) User's *MAY* optionally provide an email at signup which may be used for password resets and other notifications.
``mandatory``          User's *MUST* provide an email
``none``               User's *CANNOT* provide an email. This option usually corresponds with an alternative third-party authentication option. Otherwise user's won't be able to make accounts at all.
====================== ===========================================================


.. envvar:: DATABASE_URL

By default, the database URL used by the Django application to communicate with the Postgres database
is generated from the `Database Settings`_. This variable will override that generated database URL.

.. envvar:: DJANGOADMIN_FORCE_ALLAUTH

TODO

.. envvar:: DJANGO_ACCOUNT_ALLOW_REGISTRATION

TODO

.. envvar:: DJANGO_ADMINS

TODO

.. envvar:: DJANGO_ADMIN_URL

TODO

.. envvar:: DJANGO_ALLOWED_HOSTS

TODO

.. envvar:: DJANGO_DEBUG_TOOLBAR

TODO

.. envvar:: DJANGO_DEBUG

TODO

.. envvar:: DJANGO_DEFAULT_FROM_EMAIL

TODO

.. envvar:: DJANGO_DISCORD_CLIENT_ID

TODO

.. envvar:: DJANGO_DISCORD_CLIENT_SECRET

TODO

.. envvar:: DJANGO_DISCORD_PUBLIC_KEY

TODO

.. envvar:: DJANGO_EMAIL_BACKEND

TODO

.. envvar:: DJANGO_EMAIL_HOST_PASSWORD

TODO

.. envvar:: DJANGO_EMAIL_HOST_USER

TODO

.. envvar:: DJANGO_EMAIL_HOST

TODO

.. envvar:: DJANGO_EMAIL_PORT

TODO

.. envvar:: DJANGO_HOMEPAGE_LINKS

TODO

.. envvar:: DJANGO_SECURE_CONTENT_TYPE_NOSNIFF

TODO

.. envvar:: DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS

TODO

.. envvar:: DJANGO_SECURE_HSTS_PRELOAD

TODO

.. envvar:: DJANGO_SECURE_SSL_REDIRECT

TODO

.. envvar:: DJANGO_SERVER_EMAIL

TODO

.. envvar:: DJANGO_SETTINGS_MODULE

TODO

.. envvar:: DJANGO_SILKY_PYTHON_PROFILER_BINARY

TODO

.. envvar:: DJANGO_SILKY_PYTHON_PROFILER

TODO

.. envvar:: DJANGO_SOCIAL_LOGIN_ENABLED

TODO

.. envvar:: DJANGO_TITLE

TODO

.. envvar:: POSTGRES_DB

TODO

.. envvar:: POSTGRES_PASSWORD

TODO

.. envvar:: POSTGRES_PORT

TODO

.. envvar:: POSTGRES_USER

TODO

.. envvar:: USE_DOCKER

TODO

