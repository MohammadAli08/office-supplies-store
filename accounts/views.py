# Django
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_GET
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login as login_user, logout as logout_user
from django.contrib.auth.decorators import login_required

# Project
from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .models import User
from utils.decorators import logout_required


@require_http_methods(["GET", "POST"])
@logout_required
def register(request):
    if request.method == "GET":
        # Create an empty register form.
        form = RegisterForm()
        return render(request, "accounts/register.html", {"form": form})
    else:
        # Fill the register form by users inputted data.
        form = RegisterForm(request.POST)

        # Validate the form.
        if form.is_valid():
            # Create a new user instance.
            user = User()

            # Fill user instance fields by validated data.
            cd = form.cleaned_data
            user.email = cd["email"]
            user.set_password(cd["password"])

            # Fill the username of user with first part of his/her email.
            user.username = user.email[:user.email.index("@")]

            user.send_email_activation_code(using_time=5)
            messages.success(request, "حساب شما ایجاد شد")
            return redirect("accounts:activate_account")
        return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
@logout_required
def login(request):
    if request.method == "GET":
        # Create an empty login form.
        form = LoginForm()
        return render(request, "accounts/login.html", {"form": form})
    else:
        # Fill the login form with posted data.
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Check the email and password.
            user = User.objects.filter(email=cd["email"]).first()
            if user is None or not user.check_password(cd["password"]):
                messages.error(request, "ایمیل یا کلمه عبور اشتباه است")
            else:
                # Check if the user is active.
                if user.is_active:
                    # Login user.
                    login_user(request, user)
                    messages.success(request, "خوش آمدید")
                    return redirect("home:index")
                else:
                    messages.error(request, "حساب فعال نشده است")
        return render(request, "accounts/login.html", {"form": form})


@login_required
@require_GET
def logout(request):
    logout_user(request)
    return redirect("accounts:login")


@require_http_methods(["GET", "POST"])
@logout_required
def activate_account(request):
    if request.method == "GET":
        return render(request, "accounts/activate_account.html")
    else:
        try:
            # Try to get the inputted activation code.
            activation_code = int(request.POST.get("activation_code"))

            # Find user who has this activation code.
            user = User.objects.get(email_activation_code=activation_code)

            # Find the time difference between now and when email was sent.
            time_diff = timezone.now() - user.last_login

            # Is the time difference greater that 5 minutes?
            if time_diff.total_seconds() > 300:
                raise ValueError()
        except:
            messages.error(request, "کد یا اشتباه است یا منقضی شده است")
            return render(request, "accounts/activate_account.html")
        else:
            # Activate the account.
            user.is_active = True

            # Delete the activation code.
            user.email_activation_code = None

            # Save the changes.
            user.save()
            messages.success(request, "حساب شما فعال شد")
            return redirect("accounts:login")


@logout_required
@require_http_methods(["GET", "POST"])
def forgot_password(request):
    """Get email and send the activation code for changing password and activating account"""
    if request.method == "GET":
        form = ForgotPasswordForm()
        return render(request, "accounts/forgot_password.html", {"form": form})
    else:
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            try:
                # Try to get user.
                user = User.objects.get(email=cd["email"])
            except:
                messages.error(request, "کاربری با این ایمیل یافت نشد")
            else:
                # Find the last request time to getting activation code.
                time_diff = timezone.now() - user.last_login
                if time_diff.total_seconds() > 300:
                    user.send_email_activation_code(using_time=10)
                    messages.success(
                        request, "ایمیلی جهت بازیابی کلمه عبور برای شما ارسال شد")
                    if request.POST.get("just_activate") == "on":
                        return redirect("accounts:activate_account")
                    else:
                        return redirect("accounts:reset_password")
                else:
                    messages.error(
                        request, "برای ارسال مجدد کد باید حداقل ۵ دقیقه از ایمیل قبلی بگذرد")

        return render(request, "accounts/forgot_password.html", {"form": form})


@logout_required
@require_http_methods(["GET", "POST"])
def reset_password(request):
    """Reset password using email activation code"""
    if request.method == "GET":
        # Create an empty form.
        form = ResetPasswordForm()
        return render(request, "accounts/reset_password.html", {"form": form})
    else:
        # Fill form with inputted data.
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Try to find the user.
            try:
                user = User.objects.get(
                    email_activation_code=cd["activation_code"])
            except:
                messages.error(request, "کد اشتباه است")
            else:
                # Find the time difference between now and when the email was sent.
                time_diff = timezone.now() - user.last_login
                # Was the email sent more than 10 minuets ago?
                if time_diff.total_seconds() > 600:
                    messages.error(request, "کد منقضی شده است")
                else:
                    # Set the new password for user.
                    user.set_password(cd["password"])

                    # Activate the user account for who failed to activate their
                    # account at first.
                    user.is_active = True
                    user.email_activation_code = None
                    # Save the changes on database.
                    user.save()
                    messages.success(request, "گذرواژه با موفقیت تغییر یافت")
                    return redirect("accounts:login")
        return render(request, "accounts/reset_password.html", {"form": form})
