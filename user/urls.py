from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView, TemplateView

from .views import ActivateAccount, CreateAccount, ResendActivationEmail, view_user, edit_user


password_urls = [
    path('',
         RedirectView.as_view(
             pattern_name='dj-auth:pw_reset_start',
             permanent=False)),

    path('change/',
         auth_views.PasswordChangeView.as_view(
             template_name='user/password_change_form.html',
             success_url=reverse_lazy('dj-auth:pw_change_done')
         ),
         name='pw_change'),

    path('change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='user/password_change_done.html'
         ),
         name='pw_change_done'),

    path('reset/',
         auth_views.PasswordResetView.as_view(
             template_name='user/password_reset_form.html',
             email_template_name='user/password_reset_email.txt',
             subject_template_name='user/password_reset_subject.txt',
             success_url=reverse_lazy('dj-auth:pw_reset_sent')
         ),
         name='pw_reset_start'),

    path('reset/sent/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='user/password_reset_sent.html'
         ),
         name='pw_reset_sent'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='user/password_reset_confirm.html',
             success_url=reverse_lazy('dj-auth:pw_reset_complete')
         ),
         name='pw_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='user/password_reset_complete.html',
             extra_context={'form': AuthenticationForm}
         ),
         name='pw_reset_complete'),
]


app_name = 'user'


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dj-auth:login', permanent=False)),

    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),

    path('activate/resend/', ResendActivationEmail.as_view(), name='resend_activation'),

    path('activate', RedirectView.as_view(pattern_name='dj-auth:resend_activation',
         permanent=False)),

    path('create/', CreateAccount.as_view(), name='create'),

    path('view/', view_user, name='view'),

    path('edit/', edit_user, name='edit'),

    path('create/done/', TemplateView.as_view(template_name='user/user_create_done.html'),
         name='create_done'),

    path('login/',
         auth_views.LoginView.as_view(
             template_name='user/login.html'
         ),
         name='login'),

    path('logout/',
         auth_views.LogoutView.as_view(
             extra_context={'form': AuthenticationForm},
             template_name='user/logged_out.html'
         ),
         name='logout'),

    path('password/', include(password_urls)),
]
