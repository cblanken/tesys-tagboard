from django.conf import settings


def tagboard_settings(request):
    """Expose essential Tesy's Tagboard settings"""
    return {
        "DEFAULT_THEME": settings.DEFAULT_THEME,
        "ALTERNATE_THEME": settings.ALTERNATE_THEME,
    }
