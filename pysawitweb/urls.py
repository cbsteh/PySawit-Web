"""pysawit_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django_otp.admin import OTPAdminSite

from contact import urls as contact_urls
from organizer import urls as organizer_urls
from user import urls as user_urls
from weather import urls as weather_urls
from .views import (
    redirect_root,
    about,
    privacy_policy,
    help,
    title,
    pysawit_report,
    op_chapter,
    op_article_jtas,
    credits,
    server_error,
    not_found,
    md_cheatsheet,
    md_preview,
    help_minreq,
    help_overview,
    help_wthrrepo,
    help_wthrnasa,
    help_wthrformat,
    help_wthrprepare,
    help_wthrupload,
    help_wthrdownload,
    help_wthrimport,
    help_wthredit,
    help_wthrdelete,
    help_wthrmod,
    help_modelinput,
    help_modelrun,
    help_outputresults,
    help_outputdownload,
    help_outputparam,
    help_register,
    help_userprofile,
    help_docs,
    help_wikichanges,
    help_wikicreate,
    help_wikiedit,
    help_wikiimages,
    help_wikimove,
    help_wikinavigate,
    help_wikisettings,
)

admin.site.__class__ = OTPAdminSite

urlpatterns = [
    path('Admin1430/', admin.site.urls),

    path('contact/', include(contact_urls)),
    path('user/', include(user_urls, namespace='dj-auth')),
    path('', redirect_root),
    path('weather/', include(weather_urls)),
    path('opd/', include(organizer_urls)),

    path('title/', title, name='title'),

    path('docs/pysawit-report/', pysawit_report, name='pysawit_report'),
    path('docs/op-chapter/', op_chapter, name='op-chapter'),
    path('docs/op-article-jtas/', op_article_jtas, name='op-article-jtas'),

    path('md_cheatsheet/', md_cheatsheet, name='md_cheatsheet'),
    path('ajax/md_preview/', md_preview, name='md_preview'),

    path('notifications/', include('django_nyt.urls')),
    path('wiki/', include('wiki.urls')),

    path('help/', help, name='help'),
    path('help/minreq', help_minreq, name='help_minreq'),
    path('help/overview', help_overview, name='help_overview'),
    path('help/wthrrepo', help_wthrrepo, name='help_wthrrepo'),
    path('help/wthrnasa', help_wthrnasa, name='help_wthrnasa'),
    path('help/wthrformat', help_wthrformat, name='help_wthrformat'),
    path('help/wthrprepare', help_wthrprepare, name='help_wthrprepare'),
    path('help/wthrupload', help_wthrupload, name='help_wthrupload'),
    path('help/wthrdownload', help_wthrdownload, name='help_wthrdownload'),
    path('help/wthrimport', help_wthrimport, name='help_wthrimport'),
    path('help/wthredit', help_wthredit, name='help_wthredit'),
    path('help/wthrdelete', help_wthrdelete, name='help_wthrdelete'),
    path('help/wthrmod', help_wthrmod, name='help_wthrmod'),
    path('help/modelinput', help_modelinput, name='help_modelinput'),
    path('help/modelrun', help_modelrun, name='help_modelrun'),
    path('help/outputresults', help_outputresults, name='help_outputresults'),
    path('help/outputdownload', help_outputdownload, name='help_outputdownload'),
    path('help/outputparam', help_outputparam, name='help_outputparam'),
    path('help/register', help_register, name='help_register'),
    path('help/userprofile', help_userprofile, name='help_userprofile'),
    path('help/docs', help_docs, name='help_docs'),
    path('help/wiki/changes', help_wikichanges, name='help_wikichanges'),
    path('help/wiki/create', help_wikicreate, name='help_wikicreate'),
    path('help/wiki/edit', help_wikiedit, name='help_wikiedit'),
    path('help/wiki/images', help_wikiimages, name='help_wikiimages'),
    path('help/wiki/move', help_wikimove, name='help_wikimove'),
    path('help/wiki/navigate', help_wikinavigate, name='help_wikinavigate'),
    path('help/wiki/settings', help_wikisettings, name='help_wikisettings'),
    path('about/', about, name='about'),
    path('help/privacy/', privacy_policy, name='privacy_policy'),
    path('help/credits/', credits, name='credits'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = not_found
handler500 = server_error
