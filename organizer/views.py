import os
import pickle
import re
import tempfile
import unicodedata
from shutil import copyfileobj
from wsgiref.util import FileWrapper

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View
from openpyxl.utils.exceptions import InvalidFileException

from organizer.utils import (ObjectCreateMixin,
                             ObjectMixin,
                             ObjectUpdateMixin,
                             ObjectDetailMixin)
from user.decorators import require_authenticated_permission
from .delete_file import delete_file
from .export2xl import Export2XL
from .forms import OPDForm
from .models import OPD
from .outputsummary import OutputSummary


# CHARTS ########################################################################################


@require_authenticated_permission('organizer.add_opd')
def opd_results_annual_charts(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    groups = opd.create_annual_charts()
    if groups:
        context = {
            'opd': opd,
            'yield_list': groups[0],
            'crop_list': groups[1],
            'stress_list': groups[2],
            'water_list': groups[3],
            'meteo_list': groups[4],
        }
    else:
        context = {
            'opd': opd,
            'nodata': True,
        }

    return render(request, 'organizer/opd_results_annual_charts.html', context)


@require_authenticated_permission('organizer.add_opd')
def opd_results_daily_charts(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    groups = opd.create_daily_charts()
    if groups:
        context = {
            'opd': opd,
            'yield_list': groups[0],
            'crop_list': groups[1],
            'stress_list': groups[2],
            'water_list': groups[3],
            'meteo_list': groups[4],
        }
    else:
        context = {
            'opd': opd,
            'nodata': True,
        }

    return render(request, 'organizer/opd_results_daily_charts.html', context)


class PlotBatch(View):
    model = OPD
    template_name = 'organizer/opd_results_plot.html'
    title_plot = ''
    cht = ''

    def get_tags(self, obj):
        params = obj.get_plot_parameters(annual=(self.cht=='annual'))
        tags = ''
        for i, param in enumerate(params):
            tags += '<option value="{0}">{0}</option>'.format(param)
        return tags

    def get_context(self, obj):
        context = {
            'opd': obj,
            'title_plot': self.title_plot,
            'cht': self.cht,
            'params': self.get_tags(obj),
        }
        return context

    @method_decorator(require_authenticated_permission('organizer.add_opd'))
    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug=slug)
        return render(request, self.template_name, self.get_context(obj))

    @method_decorator(require_authenticated_permission('organizer.add_opd'))
    def post(self, request, slug):
        obj = get_object_or_404(self.model, slug=slug)
        x = request.POST['x']
        ylst = request.POST.getlist('y')
        context = self.get_context(obj)
        if x and ylst:
            chttype = request.POST.get('chart_type')
            fig = obj.plot_batch(x=x,
                                 ylst=ylst,
                                 annual=(self.cht=='annual'),
                                 chart_type=(chttype=='scatter'))
            context.update({'label': fig[0]})
            context.update({'img': fig[1]})
        else:
            msg = ('<i class="fas fa-times"></i> '
                   'Please select at least a pair of (x,y) parameters to plot.')
            messages.add_message(request, settings.PYSW_ERROR, msg)

        return render(request, self.template_name, context)


class DailyPlot(PlotBatch):
    title_plot = 'Daily Plot'
    cht = 'daily'


class AnnualPlot(PlotBatch):
    title_plot = 'Annual Plot'
    cht = 'annual'


# END OF CHARTS #################################################################################


# RUN ###########################################################################################


@require_authenticated_permission('organizer.add_opd')
def opd_confirm_run(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    return render(request, 'organizer/opd_confirm_run.html', {'opd': opd})


@require_authenticated_permission('organizer.add_opd')
def opd_request_run(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    opd.request_run()
    return render(request, 'organizer/opd_request_run.html', {})


@require_authenticated_permission('organizer.add_opd')
def opd_results(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    nrun = int(opd.nrun)
    years = int(nrun / 365)
    days = nrun % 365
    if years >= 1 and days > 0:
        nyears = '{}+ years'.format(years)
    elif years < 1 and days > 0:
        nyears = '<1 year'
    else:
        nyears = '{} year{}'.format(years, 's' if years > 1 else '')

    ini = opd.inifile(True)
    out = opd.outfile(True)
    lock = opd.lockfile(True)
    has_error = opd.has_error()
    errmsg = ''
    if has_error:
        fullpath = opd.errfile()
        with open(fullpath, 'r') as fin:
            errmsg = fin.read()

    # results ready when input and daily output files are present
    #    and lock file is absent
    if ini and out and not lock:
        with open(out, 'r') as fin:
            dt = fin.readline().rstrip('\n').lstrip('# ')   # read in date and time of run
            seed = fin.readline().rstrip('\n').lstrip('# seed ')    # read in seed number
        context = {
            'opd': opd,
            'datetime': dt,
            'seed': seed,
            'numyears': nyears,
            'numdays': nrun,
            'has_error': has_error,
            'errmsg': errmsg,
        }
    else:
        context = {
            'opd': opd,
            'norun': True,
            'has_request': opd.has_request,
            'has_lock': lock,
            'has_error': has_error,
            'errmsg': errmsg,
        }

    return render(request, 'organizer/opd_results.html', context)


@require_authenticated_permission('organizer.add_opd')
def opd_results_annual(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    context = {'opd': opd}
    return render(request, 'organizer/opd_results_annual.html', context)


@require_authenticated_permission('organizer.add_opd')
def opd_results_input(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    if opd.inifile(True):
        context = {
            'opd': opd,
        }
    else:
        context = {
            'opd': opd,
            'norun': True,
        }
    return render(request, 'organizer/opd_results_input.html', context)


@require_authenticated_permission('organizer.add_opd')
def opd_results_daily(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    dayfile = opd.outfile(True)
    tables365 = None
    context = None
    if dayfile:
        yr = request.POST.get('dropdown-years', None)
        if not yr:
            yr = 0
            outsum = OutputSummary(dayfile, 0, 0)
            outsum.load_all_values()
            tables365 = outsum.daily_as_table()
            with open(opd.picklefile(), 'wb') as pout:
                pickle.dump(tables365, pout)
        else:
            yr = int(yr) - 1
            pickfile = opd.picklefile(True)
            if pickfile:
                with open(pickfile, 'rb') as pin:
                    tables365 = pickle.load(pin)
        if tables365:
            html_table365 = tables365[yr]
            nyears = len(tables365)
            fmt = '<div class="table-div"><table class="Table">{0}</table></div>'
            context = {
                'opd': opd,
                'years': nyears,
                'current_year': str(yr + 1),
                'html_table365': fmt.format(html_table365),
            }
    if not tables365:
        context = {
            'opd': opd,
            'norun': True,
        }

    return render(request, 'organizer/opd_results_daily.html', context)

# END OF RUN #####################################################################################

# DOWNLOADS ######################################################################################


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def download(fullpath, name_to_give=''):
    if not name_to_give:
        pos = fullpath.rfind('/')
        if pos < 0:
            pos = fullpath.rfind('\\')
        filename = fullpath[pos+1:]
    else:
        filename = name_to_give

    wrapper = FileWrapper(open(fullpath, 'rb'))
    response = HttpResponse(wrapper, content_type='application/octet-stream')
    response['Content-Length'] = os.path.getsize(fullpath)
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
    return response


def download_xl(filename, name_to_give, token_value):
    fxl = tempfile.NamedTemporaryFile()
    with open(filename, 'rb') as fin:
        copyfileobj(fin, fxl)

    delete_file(filename)
    fxl.seek(0)
    response = HttpResponse(FileWrapper(fxl),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(name_to_give)
    response.set_cookie(key='fileDownloadToken', value=token_value)
    return response


@require_authenticated_permission('organizer.add_opd')
def update_xl(request, context, opd, src, sheet_name, token_value):
    template_file = 'organizer/opd_results_download.html'
    err_icon = '<i class="fas fa-times"></i> {0}'
    myfile = request.FILES.getlist('myfile')

    if not myfile:
        msg = err_icon.format('No Excel file specified.')
        messages.add_message(request, settings.PYSW_ERROR, msg)
        context['show_help'] = ''
        return render(request, template_file, context)

    user_loc = opd.runpath().rstrip('/')    # remove the '/' from the end of the directory
    fs = FileSystemStorage(location=user_loc)
    filename = user_loc + '/' + fs.save(myfile[0].name, myfile[0])

    max_size = 7
    if (fs.size(myfile[0].name) > max_size * 1024 * 1024):
        delete_file(filename)
        msg = err_icon.format('Too large! File exceeds {0} Mb limit.'.format(max_size))
        messages.add_message(request, settings.PYSW_ERROR, msg)
        context['show_help'] = ''
        return render(request, template_file, context)

    try:
        Export2XL(src, filename, sheet_name).update_xl()
    except InvalidFileException:
        delete_file(filename)
        msg = err_icon.format('Invalid or corrupted Excel file. '
                              'Only formats .xlsx, .xlsm, .xltx, and .xltm are supported.')
        messages.add_message(request, settings.PYSW_ERROR, msg)
        context['show_help'] = ''
        return render(request, template_file, context)

    return download_xl(filename, myfile[0].name, token_value)


@require_authenticated_permission('organizer.add_opd')
def opd_download_annual(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    default_name = 'annual'
    filename = slugify(opd.name) + '-' + default_name
    title = 'Download Annual Results'
    context = {
        'show_help': True,
        'opd': opd,
        'title': title,
        'header': title,
        'form_action': opd.get_download_annual_url(),
        'filename': filename,
        'wksname': default_name,
    }

    if request.method == 'POST':
        # POST
        opd.create_annual_results()
        src = opd.annfile(True)
        if 'txt' in request.POST:
            return download(src, '{}.txt'.format(filename))
        else:
            token_value = request.POST.get('token_value')
            if 'update_xl' in request.POST:
                return update_xl(request, context, opd, src, default_name, token_value)
            else:
                name = '{}.xlsx'.format(filename)
                xlname = opd.get_run_path(name)
                Export2XL(src, xlname, default_name).create_xl()
                src = xlname
                return download_xl(src, name, token_value)
    else:
        # GET
        return render(request, 'organizer/opd_results_download.html', context)


@require_authenticated_permission('organizer.add_opd')
def opd_download_daily(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    default_name = 'daily'
    filename = slugify(opd.name) + '-' + default_name
    title = 'Download Daily Results'
    context = {
        'show_help': True,
        'opd': opd,
        'title': title,
        'header': title,
        'form_action': opd.get_download_daily_url(),
        'filename': filename,
        'wksname': default_name,
    }

    if request.method == 'POST':
        # POST
        opd.create_annual_results()
        src = opd.outfile(True)
        if 'txt' in request.POST:
            return download(src, '{}.txt'.format(filename))
        else:
            token_value = request.POST.get('token_value')
            if 'update_xl' in request.POST:
                return update_xl(request, context, opd, src, default_name, token_value)
            else:
                name = '{0}.xlsx'.format(filename)
                xlname = opd.get_run_path(name)
                Export2XL(src, xlname, default_name).create_xl()
                src = xlname
                return download_xl(src, name, token_value)
    else:
        # GET
        return render(request, 'organizer/opd_results_download.html', context)


@require_authenticated_permission('organizer.add_opd')
def opd_download_input(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    fullpath = opd.inifile(True)
    return download(fullpath)

# END OF DOWNLOADS ###############################################################################


# OPD ADD, UPDATE, COPY, DELETE ##################################################################

@require_authenticated_permission('organizer.add_opd')
def opd_copy(request, slug):
    opd = get_object_or_404(OPD, slug=slug)
    opd.slug = None
    opd.save()
    msg = '<i class="fas fa-check"></i> "{}" successfully copied.'
    messages.add_message(request, settings.PYSW_SUCCESS, msg.format(opd.name))
    return render(request, 'organizer/opd_list.html',
                  {'opd_list': OPD.objects.filter(owner=opd.owner)})


@require_authenticated_permission('organizer.add_opd')
def opd_list(request):
    context = {'opd_list': OPD.objects.filter(owner=request.user)}
    return render(request, 'organizer/opd_list.html', context)


class OPDCreate(ObjectCreateMixin, View):
    form_class = OPDForm
    template_name = 'organizer/opd_edit.html'
    exit_url = reverse_lazy('organizer_opd_list')
    create_url = reverse_lazy('organizer_opd_create')


class OPDUpdate(ObjectUpdateMixin, View):
    form_class = OPDForm
    model = OPD
    template_name = 'organizer/opd_edit.html'
    exit_url = reverse_lazy('organizer_opd_list')


class OPDDetail(ObjectDetailMixin, View):
    form_class = OPDForm
    model = OPD
    template_name = 'organizer/opd_edit.html'
    exit_url = reverse_lazy('organizer_opd_list')


class OPDDelete(ObjectMixin, View):
    model = OPD
    template_name = 'organizer/opd_delete.html'
    exit_url = reverse_lazy('organizer_opd_list')

    @staticmethod
    def has_run(opd):
        return True if opd.outfile(True) else False

    @staticmethod
    def has_request(opd):
        return True if opd.has_request() else False

    @method_decorator(require_authenticated_permission('organizer.delete_opd'))
    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug=slug)
        if OPDDelete.has_run(obj):
            context = {
                'opd': obj,
                'warn_run': True,
            }
        elif OPDDelete.has_request(obj):
            context = {
                'opd': obj,
                'warn_request': True,
            }
        else:
            context = {
                'opd': obj,
            }
        return render(request, self.template_name, context)

    @method_decorator(require_authenticated_permission('organizer.delete_opd'))
    def post(self, request, slug):
        if 'cancel' in request.POST:
            return redirect(self.exit_url)

        obj = get_object_or_404(self.model, slug=slug)
        if 'default' in request.POST:
            obj.delete_run()
            obj.delete_request()
            obj.delete()
            return redirect(self.exit_url)

        context = {'opd': obj}
        if OPDDelete.has_run(obj):
            context.update({'warn_run': True})
        elif OPDDelete.has_request(obj):
            context.update({'warn_request': True})
        return render(request, self.template_name, context)

# END OF OPD ADD, UPDATE, COPY, DELETE ###########################################################
