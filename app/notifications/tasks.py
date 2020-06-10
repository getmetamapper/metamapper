# -*- coding: utf-8 -*-
from django.conf import settings

from app.notifications.email import Mailer
from metamapper.celery import app


@app.task(bind=True)
def deliver(self,
            namespace,
            template,
            subject,
            to_email,
            from_email=settings.EMAIL_DEFAULT_FROM,
            template_dict=None):
    """Celery task to asynchronously deliver an e-mail.
    """
    mailer = Mailer(namespace, template, from_email)

    if template_dict is None:
        template_dict = {}

    return mailer.deliver(to_email, subject, template_dict)
