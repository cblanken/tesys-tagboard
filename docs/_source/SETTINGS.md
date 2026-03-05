# Settings

## Environment Variables

Most settings are defined by environment variables. They may be set in an `.env` file in the project's root directory to adjust various aspects of the deployment.

See their usage details below.

### General App Settings

These environment variables are read by the Django app and thus have a corresponding value in Django accessible via `django.conf.settings`.

| Environment Variable | Django Setting | Production Default | Development Default |
| --- | --- | --- | --- |
| `ACCOUNT_EMAIL_VERIFICATION` | `DJANGO_EMAIL_VERIFICATION` | optional | optional |
| `DATABASE_URL` | `DATABASES["default"]` |  |  |
| `DJANGOADMIN_FORCE_ALLAUTH` | `DJANGO_ADMIN_FORCE_ALLAUTH` | False | False |
| `DJANGO_ACCOUNT_ALLOW_REGISTRATION` | `ACCOUNT_ALLOW_REGISTRATION` | True | True |
| `DJANGO_ADMIN_URL` | `ADMIN_URL` | `/admin` |  |
| `DJANGO_ALLOWED_HOSTS` | `ALLOWED_HOSTS` |  |  |
| `DJANGO_DEBUG_TOOLBAR` | `DEBUG_TOOLBAR` | True |  |
| `DJANGO_DEBUG` | `DEBUG` | False | True |
| `DJANGO_HOMEPAGE_LINKS` | `HOMEPAGE_LINKS` | ... | ... |
| `DJANGO_SECURE_CONTENT_TYPE_NOSNIFF` | `SECURE_CONTENT_TYPE_NOSNIFF` |  | True |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | `SECURE_HSTS_INCLUDE_SUBDOMAINS` |  | True |
| `DJANGO_SECURE_HSTS_PRELOAD` | `SECURE_HSTS_PRELOAD` |  | True |
| `DJANGO_SECURE_SSL_REDIRECT` | `SECURE_SSL_REDIRECT` |  | True |
| `DJANGO_SILKY_PYTHON_PROFILER_BINARY` | `SILKY_PYTHON_PROFILER_BINARY` | False | False |
| `DJANGO_SILKY_PYTHON_PROFILER` | `SILKY_PYTHON_PROFILER` | False | False |
| `DJANGO_SOCIAL_LOGIN_ENABLED` | `SOCIALACCOUNT_ENABLED` | True | True |
| `DJANGO_TITLE` | `TITLE` | Tesy's Tagboard | Tesy's Tagboard |
| `USE_DOCKER` |  | yes | yes |

### Email Settings

| Environment Variable | Django Setting | Production Default | Development Default |
| --- | --- | --- | --- |
| `DJANGO_DEFAULT_FROM_EMAIL` | `DEFAULT_FROM_EMAIL` |  |  |
| `DJANGO_EMAIL_BACKEND` | `EMAIL_BACKEND` | ... |  |
| `DJANGO_EMAIL_HOST_PASSWORD` | `EMAIL_HOST_PASSWORD` |  | tesys_tagboard_local_mailpit |
| `DJANGO_EMAIL_HOST_USER` | `EMAIL_HOST_USER` |  |  |
| `DJANGO_EMAIL_HOST` | `EMAIL_HOST` |  | tesys_tagboard_local_mailpit |
| `DJANGO_EMAIL_PORT` | `EMAIL_PORT` |  | 1025 |
| `DJANGO_SERVER_EMAIL` | `SERVER_EMAIL` | `DJANGO_DEFAULT_FROM_EMAIL` |  |

### Database Settings

| Environment Variable | Default        |
| -------------------- | -------------- |
| `POSTGRES_DB`        | tesys_tagboard |
| `POSTGRES_PASSWORD`  |                |
| `POSTGRES_PORT`      | 5432           |
| `POSTGRES_USER`      |                |

### Third-party Authentication

| Environment Variable | Django Setting | Production Default | Development Default |
| --- | --- | --- | --- |
| `DJANGO_DISCORD_CLIENT_ID` |  |  |  |
| `DJANGO_DISCORD_CLIENT_SECRET` |  |  |  |
| `DJANGO_DISCORD_PUBLIC_KEY` |  |  |  |
