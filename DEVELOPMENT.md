# DEVELOPMENT

Getting you're development environment setup for Tesy's Tagboard should be pretty painless.

## SYSTEM REQUIREMENTS

### DOCKER
First, this project uses Docker to setup a consistent development environment. Use [docker-compose](https://docs.docker.com/compose/) to launch all the necessary services for the app. At the time of this writing that only includes the primary Django application and a Postgres database instance, but may include more in the future.

Ensure Docker and the `docker-compose` plugin are installed on your system. Please refer to the official [Docker installation instructions](https://docs.docker.com/engine/install/) for your own system.

The docker-compose files for [dev](./docker-compose.local.yml)), [production](./docker-compose.production.yml), and [the docs](./docker-compose.docs.yml) are available in the project root directory with the related build files available in [./compose/](./compose/).

### UV (PYTHON)
TODO

### JUST
This project uses a command runner called `just`. It's not _necessary_ to use `just` to proceed with development, but it's highly recommended. Otherwise you will need to reference the `justfile` to find the appropriate commands for launching the application and performing other application management tasks. See the [installation instruction](https://just.systems/man/en/) for details on how to install `just` on your system.


## ENVIRONMENT CONFIG
The default environment files all exist under the [.envs](./.envs) directory, but these should not be modified except with the intention of changing the default configurations for all users, as these files are tracked by Git. To provide or override environment variables for your own instance simply create a `.env` in the project root directory and define all your custom environment variables there.

TODO: list relevant ENV vars and descriptions as a table


## DEBUGGING
Besides the usual browser [dev tools](https://developer.chrome.com/docs/devtools), the dev environment also includes the [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/index.html) which includes many useful tools for debugging and optimizing the Django app. Additionally, you may find it useful to set breakpoints in the django application to assess the state of variables and such. To do so, simply write `import ipdb; ipdb.set_trace()`. This will set a breakpoint launch the IPython debugger whenever that line is executed. Be sure you have launched the application with `just up-debug` so that debugging is enabled and you have access to the shell when a breakpoint is reached to perform any debugging.
