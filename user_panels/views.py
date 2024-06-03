# Python
from typing import Any

# Django
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required



@method_decorator(login_required, "dispatch")
class DashboardView(TemplateView):
    template_name = "user_panels/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        user = self.request.user
        return {"user": user}
