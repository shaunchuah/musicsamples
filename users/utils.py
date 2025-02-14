import random
import string

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse


def generate_random_password(length=20):
    characters = string.ascii_letters + string.digits
    password = "".join(random.choice(characters) for i in range(length))
    return password


def send_welcome_email(user, request):
    email_text_template = "emails/new_user_email.txt"
    email_html_template = "emails/new_user_email.html"
    protocol = request.scheme  # http or https
    domain = request.get_host()  # domain_name eg 127.0.0.1:8000
    password_reset_url = reverse("password_reset")
    full_reset_url = f"{protocol}://{domain}{password_reset_url}"
    email_subject = "Welcome to G-Trac"
    context = {
        "user": user,
        "password_reset_url": full_reset_url,
    }
    text_content = render_to_string(email_text_template, context)
    html_content = render_to_string(email_html_template, context)
    msg = EmailMultiAlternatives(
        email_subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
