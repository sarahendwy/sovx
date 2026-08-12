from .models import Setting


def site_settings(request):
    return {"site_settings": Setting.objects.first()}
