# Settings

## Environment Variables

Most settings are defined by environment variables. They may be set in an `.env` file in the project's root directory to adjust various aspects of the deployment.

See their usage details below.

### Django App Settings

These environment variables are read by the Django app and thus have a corresponding value in Django accessible via `django.conf.settings`.

#### Base

These environment variables affect both production and development deployments.

| Environment Variable | Django Setting | Production Default | Development Default |
| --- | --- | --- | --- |
| `DATABASE_URL` | `DATABASES["default"]` |  |  |
| `DJANGOADMIN_FORCE_ALLAUTH` | `DJANGO_ADMIN_FORCE_ALLAUTH` | False | False |
| `DJANGO_ACCOUNT_ALLOW_REGISTRATION` | `ACCOUNT_ALLOW_REGISTRATION` | True | True |
| `DJANGO_ADMIN_URL` | `ADMIN_URL` | `/admin` |  |
| `DJANGO_DEBUG` | `DEBUG` | False | True |
| `DJANGO_DISCORD_CLIENT_ID` |  |  |  |
| `DJANGO_DISCORD_CLIENT_SECRET` |  |  |  |
| `DJANGO_DISCORD_PUBLIC_KEY` |  |  |  |
| `DJANGO_EMAIL_BACKEND` | `EMAIL_BACKEND` | ... |  |
| `DJANGO_SILKY_PYTHON_PROFILER_BINARY` | `SILKY_PYTHON_PROFILER_BINARY` | False | False |
| `DJANGO_SILKY_PYTHON_PROFILER` | `SILKY_PYTHON_PROFILER` | False | False |
| `DJANGO_SOCIAL_LOGIN_ENABLED` |  | True | True |
| `POSTGRES_DB` |  | tesys_tagboard |  |
| `POSTGRES_PASSWORD` |  |  |  |
| `POSTGRES_PORT` |  | 5432 |  |
| `POSTGRES_USER` |  |  |  |
| `USE_DOCKER` |  | yes | yes |
| `DJANGO_HOMEPAGE_LINKS` | `HOMEPAGE_LINKS` | ... | ... |
| `DJANGO_ALLOWED_HOSTS` | `ALLOWED_HOSTS` |  |  |
| `DJANGO_SECURE_SSL_REDIRECT` | `SECURE_SSL_REDIRECT` |  | True |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | `SECURE_HSTS_INCLUDE_SUBDOMAINS` |  | True |
| `DJANGO_SECURE_HSTS_PRELOAD` | `SECURE_HSTS_PRELOAD` |  | True |
| `DJANGO_SECURE_CONTENT_TYPE_NOSNIFF` | `SECURE_CONTENT_TYPE_NOSNIFF` |  | True |
| `DJANGO_DEBUG_TOOLBAR` | `DEBUG_TOOLBAR` | True |  |
