import json
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import View

from .forms import ContactForm


class ContactView(View):
    form_class = ContactForm
    template_name = 'contact/contact_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        bound_form = self.form_class(request.POST)
        if bound_form.is_valid():
            # begin reCAPTCHA validation
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urlencode(values).encode('utf-8')
            req = Request(url, data)
            response = urlopen(req)
            result = json.load(response)
            # end reCAPTCHA validation

            if result['success']:
                mail_sent = bound_form.send_mail()
                if mail_sent:
                    msg = '<i class="fas fa-check"></i> Email successfully sent.'
                    messages.add_message(request, settings.PYSW_SUCCESS, msg)
                    return redirect('organizer_opd_list')
            else:
                msg = '<i class="fas fa-times"></i> Invalid reCAPTCHA. Please try again.'
                messages.add_message(request, settings.PYSW_ERROR, msg)

        return render(request, self.template_name, {'form': bound_form})
