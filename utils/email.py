# Django
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email(subject:str, to:list, template_name:str, template_context:dict):
    # Convert the rendered template to string.
    html_message = render_to_string(template_name, template_context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER

    send_mail(subject, plain_message, from_email,
              recipient_list=to, html_message=html_message)
