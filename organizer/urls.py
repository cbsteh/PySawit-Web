from django.urls import path

from .views import (
    OPDCreate,
    OPDDelete,
    OPDDetail,
    OPDUpdate,
    opd_copy,
    opd_list,
    opd_confirm_run,
    opd_request_run,
    opd_results,
    opd_results_input,
    opd_results_daily,
    opd_results_annual,
    opd_results_annual_charts,
    opd_results_daily_charts,
    DailyPlot,
    AnnualPlot,
    opd_download_input,
    opd_download_daily,
    opd_download_annual,
)


urlpatterns = [
    path('', opd_list, name='organizer_opd_list'),
    path('create/', OPDCreate.as_view(), name='organizer_opd_create'),

    path('<uuid:slug>/', OPDDetail.as_view(), name='organizer_opd_detail'),
    path('<uuid:slug>/copy/', opd_copy, name='organizer_opd_copy'),
    path('<uuid:slug>/delete/', OPDDelete.as_view(), name='organizer_opd_delete'),
    path('<uuid:slug>/update/', OPDUpdate.as_view(), name='organizer_opd_update'),

    path('<uuid:slug>/run/confirm', opd_confirm_run, name='organizer_opd_confirm_run'),
    path('<uuid:slug>/run/request', opd_request_run, name='organizer_opd_request_run'),

    path('<uuid:slug>/results/', opd_results, name='organizer_opd_results'),
    path('<uuid:slug>/results/input/', opd_results_input, name='organizer_opd_results_input'),
    path('<uuid:slug>/results/daily/', opd_results_daily, name='organizer_opd_results_daily'),
    path('<uuid:slug>/results/annual/', opd_results_annual, name='organizer_opd_results_annual'),

    path('<uuid:slug>/results/annual/charts/', opd_results_annual_charts,
         name='organizer_opd_results_annual_charts'),
    path('<uuid:slug>/results/daily/charts/', opd_results_daily_charts,
         name='organizer_opd_results_daily_charts'),

    path('<uuid:slug>/results/daily/plot/', DailyPlot.as_view(),
         name='organizer_opd_results_daily_plot'),
    path('<uuid:slug>/results/annual/plot/', AnnualPlot.as_view(),
         name='organizer_opd_results_annual_plot'),

    path('<uuid:slug>/download/input/', opd_download_input, name='organizer_opd_download_input'),
    path('<uuid:slug>/download/daily/', opd_download_daily, name='organizer_opd_download_daily'),
    path('<uuid:slug>/download/annual/', opd_download_annual, name='organizer_opd_download_annual'),
]
