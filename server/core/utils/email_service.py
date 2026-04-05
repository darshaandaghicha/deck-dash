from typing import List, Dict, Any

from django.template.loader import render_to_string
from django.utils.html import strip_tags

from config.settings import DEFAULT_FROM_EMAIL
from django.core.mail import EmailMultiAlternatives


class EmailService:
    @staticmethod
    def send_email(
        to: List[str], subject: str, template_name: str, context: Dict[str, Any]
    ) -> int:
        template_name = f"emails/{template_name.lower().strip()}.html"
        sender: str = DEFAULT_FROM_EMAIL
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=sender, to=to
        )
        email.attach_alternative(html_content, "text/html")
        return email.send()
