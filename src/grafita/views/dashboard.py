from typing import Final

from django.views.generic.base import TemplateView


class Dashboard(TemplateView):
    # own
    url: Final = "/dashboard"

    # overridden
    template_name: Final = 'dashboard.html'
