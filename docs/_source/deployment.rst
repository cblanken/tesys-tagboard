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

Configure Environment
~~~~~~~~~~~~~~~~~~~~~

TODO


Bring up the app and all it’s required services.

.. code:: bash

   docker compose -f docker-compose.production.yml up -d

Then run database migrations to initialize the database.

.. code:: bash

   docker compose -f docker-compose.production.yml exec django python manage.py migrate

Then create an admin user following the command prompts of ``createsuperuser``.

.. code:: bash

   $ docker compose -f docker-compose.production.yml exec django python manage.py createsuperuser

See all the available application settings in `Settings <SETTINGS.md>`__

Logs
----

Run the following to view the logs of all running services.
.. code:: bash

   $ docker compose -f docker-compose.production.yml logs -f

Alternatively select a specific service by name to only show logs from that service.
For example showing logs of just the Django app.
.. code:: bash

   $ docker compose -f docker-compose.production.yml logs -f django

Some Recommendations
~~~~~~~~~~~~~~~~~~~~

Following are a few recommendations for deployment.

Reverse proxy
^^^^^^^^^^^^^

TODO

Admin Endpoint
^^^^^^^^^^^^^^

Set the admin endpoint to a long randomized, alphanumeric value to avoid
scanning or brute-force attempts. The endpoint for the admin dashboard
can be set with the :ref:`DJANGO_ADMIN_URL` environment variable, which
defaults to ``/admin``.

Set a Complex Admin Password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set a long, complex password for your superuser / admin account. The
``createsuperuser`` command allows you to bypass password complexity
requirements, but I recommend you make a sufficiently long and complex
password. Preferably more than 24 characters.

Schedule regular database backups.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TODO

Require email confirmation
^^^^^^^^^^^^^^^^^^^^^^^^^^
Email confirmation is required by default, but it can be disabled.
Setup one of the :ref:`supported email providers <supported-email-providers>` or use your own SMTP
server.


Deployment without cloning?
---------------------------

TODO

Configuring Tesy's Tagboard with a CDN
--------------------------------------

TODO
