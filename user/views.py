import json
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View

from .forms import ResendActivationEmailForm, UserCreationForm, UserForm, UserProfileForm
from .models import UserProfile
from .utils import MailContextViewMixin
from weather.models import Weather
from organizer.models import OPD
from wiki.models.article import Article


@login_required
def view_user(request):
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = UserProfile()
        profile.user = request.user
        profile.save()

    try:
        avatar_url = profile.avatar.url
        avatar_width = profile.avatar.width
    except ValueError:
        avatar_url = ''
        avatar_width = 200

    user_weatherlist = Weather.objects.filter(owner=request.user)
    user_opdlist = OPD.objects.filter(owner=request.user)
    user_articlelist = Article.objects.filter(owner=request.user)

    context = {
        'user': request.user,
        'avatar_url': avatar_url,
        'avatar_width': avatar_width,
        'user_opdlist': user_opdlist,
        'user_weatherlist': user_weatherlist,
        'user_articlelist': user_articlelist,
    }
    return render(request, 'user/user_view.html', context)


@login_required
def edit_user(request):
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = UserProfile()
        profile.user = request.user
        profile.save()

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=request.user)
        profileform = UserProfileForm(request.POST, request.FILES,
                                      user=request.user, instance=profile)
        if form.is_valid() and profileform.is_valid():
            form.save()
            profileform.save()
            msg = '<i class="fas fa-check"></i> Your user profile has been successfully updated.'
            messages.add_message(request, settings.PYSW_SUCCESS, msg)
            return redirect('organizer_opd_list')
        else:
            msg = ('<i class="fas fa-times"></i> '
                   'Error updating your profile. Please try again later.')
            messages.add_message(request, settings.PYSW_ERROR, msg)

    try:
        avatar_url = profile.avatar.url
    except ValueError:
        avatar_url = ''

    context = {
        'user': request.user,
        'avatar_url': avatar_url,
    }
    return render(request, 'user/user_edit.html', context)


class ActivateAccount(View):
    success_url = reverse_lazy('dj-auth:login')
    template_name = 'user/user_activate.html'

    @method_decorator(never_cache)
    def get(self, request, uidb64, token):
        usermodel = get_user_model()
        try:
            # Django 2.0: urlsafe_base64_decode() -> bytestring in Py3
            uid = urlsafe_base64_decode(uidb64).decode()
            user = usermodel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, usermodel.DoesNotExist):
            user = None
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            msg = '<i class="fas fa-check"></i> Your account has been activated! Please log in.'
            messages.add_message(request, settings.PYSW_SUCCESS, msg)
            return redirect(self.success_url)
        else:
            return TemplateResponse(request, self.template_name)


class CreateAccount(MailContextViewMixin, View):
    form_class = UserCreationForm
    profileform_class = UserProfileForm
    success_url = reverse_lazy('dj-auth:create_done')
    template_name = 'user/user_create.html'

    @method_decorator(csrf_protect)
    def get(self, request):
        context = {}
        return TemplateResponse(request, self.template_name, context)

    @method_decorator(csrf_protect)
    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    def post(self, request):
        def set_context(key):
            try:
                context[key] = bound_form.cleaned_data[key]
            except KeyError:
                pass    # ignore key due to invalid field data entered by user

        bound_form = self.form_class(request.POST, request.FILES)
        bound_profileform = self.profileform_class(request.POST, request.FILES,
                                                   user=request.user)
        context = {}
        bset = False

        if bound_form.is_valid() and bound_profileform.is_valid():
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
                bf = bound_form.save(**self.get_save_kwargs(request))

                profile = UserProfile()
                profile.avatar = bound_profileform.cleaned_data['avatar']
                profile.user = bf
                profile.save()

                if bound_form.mail_sent:  # mail sent?
                    return redirect(self.success_url)
                else:
                    errs = bound_form.non_field_errors()
                    msg = '<i class="fas fa-times"></i> {}'
                    for err in errs:
                        messages.add_message(request, settings.PYSW_ERROR, msg.format(err))
                    return redirect('dj-auth:resend_activation')
            else:
                msg = '<i class="fas fa-times"></i> Invalid reCAPTCHA. Please try again.'
                messages.add_message(request, settings.PYSW_ERROR, msg)
                bset = True
        else:
            msg = '<i class="fas fa-times"></i> Invalid registration details. Please try again.'
            messages.add_message(request, settings.PYSW_ERROR, msg)
            bset = True

        if bset:
            set_context('username')
            set_context('first_name')
            set_context('last_name')
            set_context('email')

        return TemplateResponse(request, self.template_name, context)


class ResendActivationEmail(MailContextViewMixin, View):
    form_class = ResendActivationEmailForm
    success_url = reverse_lazy('dj-auth:login')
    template_name = 'user/resend_activation.html'

    @method_decorator(csrf_protect)
    def get(self, request):
        return TemplateResponse(request, self.template_name, {'form': self.form_class()})

    @method_decorator(csrf_protect)
    def post(self, request):
        bound_form = self.form_class(request.POST)
        if bound_form.is_valid():
            user = bound_form.save(**self.get_save_kwargs(request))
            if user is not None and not bound_form.mail_sent:
                errs = bound_form.non_field_errors()
                msg = '<i class="fas fa-times"></i> {}'
                for err in errs:
                    messages.add_message(request, settings.PYSW_ERROR, msg.format(err))
                if errs:
                    bound_form.errors.pop('__all__')
                return TemplateResponse(request, self.template_name, {'form': bound_form})

        msg = '<i class="fas fa-check"></i> Activation email has been sent.'
        messages.add_message(request, settings.PYSW_SUCCESS, msg)
        return redirect(self.success_url)
