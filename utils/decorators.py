from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import redirect


# Auth

def logout_required(func):
    def wrap(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:index")
        return func(request, *args, **kwargs)
    return wrap


# View

def ajax_required(func):
    def wrap(request: HttpRequest, *args, **kwargs):
        #
        if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return HttpResponseBadRequest()
        return func(request, *args, **kwargs)
    return wrap
