# -*- coding: utf-8 -*-
import datetime as dt

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string

from email.mime.base import MIMEBase


class Mailer(object):
    """Default mailer class for sending messages to an end user.
    """
    def __init__(self, namespace, template, from_email=settings.EMAIL_DEFAULT_FROM):
        self.namespace = namespace
        self.template = template
        self.from_email = from_email
        self.calendar_attachment = None

    def set_from_email(self, from_email):
        self.from_email = from_email

    def deliver(self, to_email, subject, template_dict):
        message = self.create_message(to_email, subject, template_dict)
        if self.calendar_attachment:
            message.attach(self.calendar_attachment)
        return message.send()

    def create_message(self, to_email, subject, template_dict):
        default_params = {
            'domain': settings.WEBSERVER_ORIGIN,
            'now': dt.datetime.utcnow(),
        }

        template_dict.update(default_params)
        text_content = self.render_content_as_text(template_dict)
        html_content = self.render_content_as_html(template_dict)

        mail_kwargs = {
            'subject': subject,
            'body': text_content,
            'from_email': self.from_email,
            'to': [to_email],
        }

        message = EmailMultiAlternatives(**mail_kwargs)
        message.attach_alternative(html_content, 'text/html')
        return message

    def attach_calendar(self, content, method='REQUEST', name='invite.ics'):
        icspart = MIMEBase('text', 'calendar', method=method, name=name)
        icspart.set_payload(content)
        icspart.add_header('Content-Transfer-Encoding', '8bit')
        icspart.add_header('Content-class', 'urn:content-classes:calendarmessage')
        self.calendar_attachment = icspart

    def render_content_as_text(self, params):
        return render_to_string('%s/%s.txt' % (self.namespace, self.template), params)

    def render_content_as_html(self, params):
        return render_to_string('%s/%s.html' % (self.namespace, self.template), params)
