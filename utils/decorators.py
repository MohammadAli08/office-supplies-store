from django.shortcuts import redirect

# Auth

def logout_required(func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return func(request, *args, **kwargs)
    return wrap
