# DEVELOPMENT

Getting your development environment setup for Tesy's Tagboard should be pretty painless.

First off, the initial structure for the app was based on [cookiecutter-django](https://cookiecutter-django.readthedocs.io/), so much of the structure of the application still follows that template. Of course, refer to the documentation here first, but the cookiecutter-django docs may also be helpful.

## SYSTEM REQUIREMENTS
First, this project uses Docker to setup a consistent development environment. So, all system dependencies are handled by Docker with the exception of the command runner [just](#just) which is used to handle various scripts for actions such as bringing up and down the docker dev environment, running tests, and loading demo data etc.

### DOCKER
Please refer to the official [Docker installation instructions](https://docs.docker.com/engine/install/) to install Docker on your own system. If you are running a Windows system, the preferred method is to install [Docker Desktop](https://docs.docker.com/desktop/).

The [docker-compose](https://docs.docker.com/compose/) plugin is used to launch all the necessary services for the app, so be sure to install it as well.


### JUST
This project uses a command runner called `just`. It's not _necessary_ to use `just` to proceed with development, but it's highly recommended. Otherwise you will need to reference the `justfile` to find the appropriate commands for launching the application and performing other application management tasks. See the [installation instruction](https://just.systems/man/en/) for details on how to install `just` on your system.

## LAUNCHING THE APP

After you've installed the [required dependencies](#system-requirements), then launching the application should be as simple as running the command `just up` from the terminal located in the project directory. On first execution this may take some to build the dev container from scratch. Expect from 5 to 10 minutes, so maybe go grab a coffee or keep reading :)


## ENVIRONMENT CONFIG

The default development environment env files are located at `.envs/.local/`

The default environment files all exist under the [.envs](./.envs) directory, but these should not be modified except with the intention of changing the default configurations for all users, as these files are tracked by Git. To provide or override environment variables for your own instance simply create a `.env` in the project root directory and define all your custom environment variables there.

For a detailed description of all the available environment variables, please see the [deployment docs](/DEPLOYMENT.md#configuration).


## DEBUGGING
Besides the usual browser [dev tools](https://developer.chrome.com/docs/devtools), the dev environment also includes the [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/index.html) which includes many useful tools for debugging and optimizing the Django app. Additionally, you may find it useful to set breakpoints in the django application to troubleshoot errors. To do so, simply write `import ipdb; ipdb.set_trace()`. This will set a breakpoint to launch the IPython debugger wherever that line is executed. Be sure you have launched the application with `just up-debug` so that debugging is enabled and you have access to the shell when a breakpoint is reached to perform any debugging.

## PRE-COMMIT
The linting and code formatting for this project is handled by `pre-commit`. Please see the [official installation instruction](https://pre-commit.com/#installation) to install it for your system. All of the configured pre-commit hooks may be found in the [.pre-commit.config-yml](/.pre-commit-config-yml) config file.

Once you've installed `pre-commit`, you may then install the git hook scripts by running `pre-commit install` from the project's root directory. This will ensure all the required pre-commit hooks will run every time you make a commit. If you'd like to catch any pre-commit errors before actually attempting a `git commit` or prefer not to install git hooks, you may run the pre-commit hooks manually with `pre-commit run`.

## RUNNING TESTS
Tests should be run with `just test`. This will launch pytest in the dev container with a default number of workers. If you have many cores on your machine, you may wish to increase the worker count with the `-n` flag. For example, running `just test -n 8` which may decrease the test runtime though you will need to experiment with the number for the best results on your own machine.

All tests should pass or be updated if required before a PR is merged. I recommend running the tests before each commit (when reasonable) and certainly before pushing to your feature branch.

## LOCAL DEV WITHOUT DOCKER
It is, of course, possible to develop the application without Docker, but it is not recommended or supported. You will have to resolve issues you encounter on your own. Regardless, here is a brief breakdown of what you will need to run the application locally without Docker.

### UV (PYTHON)
TODO

### DATABASE (Postgres)
TODO
