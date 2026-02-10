from django.conf import settings

def get_environment(request):
    """
    Returns environment labels for the Django Unfold admin.
    """
    if settings.DEBUG:
        return ["Development", "info"]  # info = blue/gray label
    return ["Production", "success"]  # success = green label
