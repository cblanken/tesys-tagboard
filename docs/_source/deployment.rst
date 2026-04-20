Deployment Guide
================

Here you will find all the instructions for deploying your own instance of Tesy’s Tagboard.

System Requirements
-------------------
TODO

-  Storage
-  RAM

Deployment Process
------------------

The simplest way to get Tesy’s Tagboard up and running is with `Docker
Compose <https://docs.docker.com/compose/>`__. First, clone the
repository.

Configure
~~~~~~~~~

The configuration files for Tesy's Tagboard are all located in the ``.envs/.production/`` directory.
For each service there will be a ``service.example`` file which contains a default configuration.
Copy these files to the same location without ``.example`` extension to modify any of the settings.
You should end up with a ``.envs`` directory that looks like this.

.. code:: bash

    .envs/.production/
    ├── .django
    ├── .django.example
    ├── .postgres
    └── .postgres.example

The application should run out-of-the-box with the default configuration, but you will want to review
each of the custom configuration files to update the environment variables where needed.

In particular, the following variables should be customized for your own deployment of the app.

- :envvar:`DJANGO_SECRET_KEY`: randomly generate a long alphanumeric string
- :envvar:`DJANGO_ALLOWED_HOSTS`: add the domain you'll be hosting the app from
- :envvar:`DJANGO_TITLE`: update the app title
- :envvar:`DJANGO_DEFAULT_FROM_EMAIL`: if you're planning to support emails for accounts and all the related ``DJANGO_EMAIL_`` variables to configure email sending


Starting the Application
~~~~~~~~~~~~~~~~~~~~~~~~

Bring up the app along with any other required services with ``docker-compose``.

.. code:: bash

   docker compose -f docker-compose.production.yml up -d

The first time the application is started, the database migrations must be run to initialize the database.

.. code:: bash

   docker compose -f docker-compose.production.yml exec django python manage.py migrate

Create an admin user following the command prompts of the ``createsuperuser`` command.

.. code:: bash

   docker compose -f docker-compose.production.yml exec django python manage.py createsuperuser

See all the available application settings in :doc:`configuration/settings` and adapt them to your needs.

Logs
----

If you can't connect to the application after following the previous steps, then you will want to
investigate the logs for any error messages. Run the following commant to view the logs of all
running services.

.. code:: bash

   docker compose -f docker-compose.production.yml logs -f

Alternatively select a specific service by name to only show logs from that service.
For example showing logs of just the Django app.

.. code:: bash

   docker compose -f docker-compose.production.yml logs -f django

Some Recommendations
~~~~~~~~~~~~~~~~~~~~

These are a few recommendations for deployment. You are free to ignore them if you wish, but don't say I didn't warn you.

Reverse proxy
^^^^^^^^^^^^^

TODO

Admin Endpoint
^^^^^^^^^^^^^^

Set the admin endpoint to a long randomized, alphanumeric value to avoid
scanning or brute-force attempts. The endpoint for the admin dashboard
can be set with the :envvar:`DJANGO_ADMIN_URL` environment variable, which
defaults to ``/admin``.

Set a Complex Admin Password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set a long, complex password for your superuser / admin account. The
``createsuperuser`` command allows you to bypass password complexity
requirements, but I recommend you make a sufficiently long and complex
password. If you're unsure of what constitutes a strong password, please
read through the `password strength recommendations <https://www.cisa.gov/audiences/small-and-medium-businesses/secure-your-business/require-strong-passwords>`__ by CISA.

Schedule regular database backups.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TODO

Require email confirmation
^^^^^^^^^^^^^^^^^^^^^^^^^^
Email confirmation is required by default, but it can be disabled.
Setup one of the :ref:`supported email providers <supported-email-providers>` or use your own SMTP
server.


Configuring Tesy's Tagboard with a CDN
--------------------------------------

TODO
