import logging
import traceback
from logging import CRITICAL, ERROR
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

logger = logging.getLogger(__name__)


class ActivationMailFormMixin:
    mail_validation_error = ''

    @staticmethod
    def log_mail_error(**kwargs):
        msg_list = [
            'Activation email did not send.\n',
            'from_email: {from_email}\n'
            'subject: {subject}\n'
            'message: {message}\n',
        ]
        recipient_list = kwargs.get('recipient_list', [])
        for recipient in recipient_list:
            msg_list.insert(1, 'recipient: {r}\n'.format(r=recipient))
        if 'error' in kwargs:
            level = ERROR
            error_msg = 'error: {0.__class__.__name__}\nargs: {0.args}\n'
            error_info = error_msg.format(kwargs['error'])
            msg_list.insert(1, error_info)
        else:
            level = CRITICAL
        msg = ''.join(msg_list).format(**kwargs)
        logger.log(level, msg)

    @property
    def mail_sent(self):
        if hasattr(self, '_mail_sent'):
            return self._mail_sent
        return False

    @mail_sent.setter
    def mail_sent(self, value):
        raise TypeError('Cannot set mail_sent attribute.')

    @staticmethod
    def get_message(**kwargs):
        email_template_name = kwargs.get('email_template_name')
        context = kwargs.get('context')
        return render_to_string(email_template_name, context)

    @staticmethod
    def get_subject(**kwargs):
        subject_template_name = kwargs.get('subject_template_name')
        context = kwargs.get('context')
        subject = render_to_string(subject_template_name, context)
        # subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        return subject

    @staticmethod
    def get_context_data(request, user, context=None):
        if context is None:
            context = dict()
        current_site = get_current_site(request)
        if request.is_secure():
            protocol = 'https'
        else:
            protocol = 'http'
        token = token_generator.make_token(user)
        # Django 2.0 change:
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        context.update({
            'domain': current_site.domain,
            'protocol': protocol,
            'site_name': current_site.name,
            'token': token,
            'uid': uid,
            'user': user,
        })
        return context

    @staticmethod
    def _send_mail(request, user, **kwargs):
        kwargs['context'] = ActivationMailFormMixin.get_context_data(request, user)
        mail_kwargs = {
            "subject": ActivationMailFormMixin.get_subject(**kwargs),
            "message": ActivationMailFormMixin.get_message(**kwargs),
            "from_email": settings.DEFAULT_FROM_EMAIL,
            "recipient_list": [user.email],
        }
        try:
            # number_sent will be 0 or 1
            number_sent = send_mail(**mail_kwargs)
        except Exception as error:
            ActivationMailFormMixin.log_mail_error(error=error, **mail_kwargs)
            if isinstance(error, BadHeaderError):
                err_code = 'badheader'
            elif isinstance(error, SMTPException):
                err_code = 'smtperror'
            else:
                err_code = 'unexpectederror'
            return False, err_code
        else:
            if number_sent > 0:
                return True, None
        ActivationMailFormMixin.log_mail_error(**mail_kwargs)
        return False, 'unknownerror'

    def send_mail(self, user, **kwargs):
        request = kwargs.pop('request', None)
        if request is None:
            tb = traceback.format_stack()
            tb = ['  ' + line for line in tb]
            logger.warning('send_mail called without request.\nTraceback:\n{}'.format(''.join(tb)))
            self._mail_sent = False
            return self.mail_sent, 'norequest'
        self._mail_sent, error = ActivationMailFormMixin._send_mail(request, user, **kwargs)
        return self.mail_sent, error


class MailContextViewMixin:
    email_template_name = 'user/email_create.txt'
    subject_template_name = 'user/subject_create.txt'

    def get_save_kwargs(self, request):
        return {
            'email_template_name': self.email_template_name,
            'request': request,
            'subject_template_name': self.subject_template_name,
        }
