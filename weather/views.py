import os
import uuid
from collections import OrderedDict
from wsgiref.util import FileWrapper

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View

from organizer.delete_file import delete_file
from user.decorators import require_authenticated_permission
from .forms import WeatherForm
from .models import Weather
from .nasa import NASAData

from shutil import copyfileobj
import tempfile
from django.core.files.storage import FileSystemStorage
from organizer.export2xl import Export2XL
from openpyxl.utils.exceptions import InvalidFileException


@require_authenticated_permission('weather.add_weather')
def weather_detail(request, slug):
    wthr = get_object_or_404(Weather, slug=slug)
    ret = wthr.display_weather()
    if not ret[0]:
        messages.add_message(request, settings.PYSW_ERROR, ret[1])
        table_data = ('<em>No data.</em><div class="trash-it">'
                      '<i class="far fa-times-circle faa-pulse animated"></i> '
                      'delete this file</div')
        stats_list = []
    else:
        table_data = ret[1]
        gen = []
        for key, dct in ret[3].items():
            if key == 'tmin':
                key = 'Min. Air Temperature'
            elif key == 'tmax':
                key = 'Max. Air Temperature'
            elif key == 'wind':
                key = 'Wind Speed'
            elif key == 'rain':
                key = 'Rain'
            gen.append((key, dct))
        stats_list = OrderedDict([(g[0], g[1]) for g in gen])

    return render(request, 'weather/weather_detail.html',
                  {
                      'weather': wthr,
                      'dep_list': wthr.opd.all(),
                      'table_data': table_data,
                      'charts_list': ret[2],
                      'stats_list': stats_list,
                  })


@require_authenticated_permission('weather.add_weather')
def weather_list(request):
    wthrlst = Weather.objects.filter(owner=request.user)
    return render(request, 'weather/weather_list.html', {'weather_list': wthrlst})


@require_authenticated_permission('weather.add_weather')
def weather_upload(request):
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(reverse('weather_list'))

        form = WeatherForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            new_form = form.save()
            return redirect(new_form)
    else:
        form = WeatherForm()

    path = os.path.join(settings.MEDIA_ROOT, 'repository/weather/').replace('\\', '/')
    filelst = os.listdir(path)
    dct = {}
    for file in filelst:
        f = path + file
        lst = []
        with open(f, 'r') as fin:
            for line in fin:
                ln = line.strip(' ')
                if ln[0] == '#':
                    ln = ln.strip(' # ').replace('\n', '')
                    lst.append(ln)
                else:
                    break
        if lst:
            desc = '; '.join(lst)
        else:
            desc = 'no description given'
        dct.update({file: desc})

    return render(request, 'weather/weather_upload.html',
                  {
                      'form': form,
                      'path': path,
                      'dct': dct,
                  })


class WeatherDelete(View):
    model = Weather
    template_name = 'weather/weather_delete.html'
    success_url = reverse_lazy('weather_list')

    @method_decorator(require_authenticated_permission('weather.delete_weather'))
    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug=slug)
        context = {self.model.__name__.lower(): obj}
        if obj.opd.all():
            context.update({'nodelete': True})
        return render(request, self.template_name, context)

    @method_decorator(require_authenticated_permission('weather.delete_weather'))
    def post(self, request, slug):
        if 'cancel' in request.POST:
            return redirect(reverse('weather_list'))

        obj = get_object_or_404(self.model, slug=slug)
        if not obj.opd.all():
            try:
                delete_file(os.path.join(settings.MEDIA_ROOT, obj.weatherfile.name))
                obj.delete()
                msg = '<i class="fas fa-check"></i> File has been deleted.'
                messages.add_message(request, settings.PYSW_SUCCESS, msg)
            except IOError:
                msg = ('<i class="fas fa-times"></i> "{}" cannot be deleted '
                       'due to file error. File could currently be in use. '
                       'Try deleting the file later. If this problem persist, '
                       'please contact the admistrator.')
                messages.add_message(request, settings.PYSW_ERROR, msg.format(obj.name))

        return redirect(self.success_url)


class WeatherUpdate(View):
    form_class = WeatherForm
    model = Weather
    template_name = 'weather/weather_edit.html'
    exit_url = reverse_lazy('weather_list')

    @method_decorator(require_authenticated_permission('weather.change_weather'))
    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug=slug)
        context = {
            'form': self.form_class(instance=obj),
            'form_action': obj.get_update_url,
        }
        return render(request, self.template_name, context)

    @method_decorator(require_authenticated_permission('weather.change_weather'))
    def post(self, request, slug):
        if 'cancel' in request.POST:
            return redirect(self.exit_url)

        obj = get_object_or_404(self.model, slug=slug)
        bound_form = self.form_class(request.POST, instance=obj, request=request)
        if bound_form.is_valid():
            new_object = bound_form.save()
            msg = '<i class="fas fa-check"></i> File descripton of "{}" successfully saved.'
            messages.add_message(request, settings.PYSW_SUCCESS, msg.format(new_object.name))
            return redirect(new_object.get_update_url())
        else:
            context = {
                'form': bound_form,
                'form_action': obj.get_update_url,
            }
            return render(request, self.template_name, context)


@require_authenticated_permission('weather.add_weather')
def weather_access_nasa(request):
    c = request.GET.get('calibrate_check', True)
    is_calibrate = c.lower() in ['1', 'true']

    lat = float(request.GET.get('lat', 0.0))
    lng = float(request.GET.get('lng', 0.0))
    start_year = int(request.GET.get('start_year', 0))
    year_num = int(request.GET.get('year_num', 0))
    end_year = start_year + year_num - 1
    start_date = int('{}0101'.format(start_year))
    end_date = int('{}1231'.format(end_year))

    temp_filename = str(uuid.uuid1()) + '.txt'
    temp_path = '{0}/nasa/{1}'.format(settings.MEDIA_ROOT, temp_filename)

    sitename = request.GET.get('sitename', '').strip()
    if not sitename:
        sitename = 'site'
    str_start = str(start_year)[2:]
    str_end = str(end_year)[2:]
    wthr_filename = '{}-{}-{}-{}-{}.txt'.format(sitename, lat, lng, str_start, str_end)
    wthr_desc = '{}; GPS ({}, {}); Years ({} - {})'.format(sitename,
                                                           lat, lng,
                                                           start_year, end_year)
    dct = {
        'weather_filename': temp_path,
        'start_date': start_date,
        'end_date': end_date,
        'lat': lat,
        'lon': lng,
        'calibrate_check': is_calibrate,
    }
    nasaobj = NASAData(dct)
    data = {
        'is_valid': nasaobj.status[0],
        'err_msg': nasaobj.status[1],
        'wthr_filename': wthr_filename,
        'temp_filename': temp_filename,
        'wthr_desc': wthr_desc,
    }
    return JsonResponse(data)


@require_authenticated_permission('weather.add_weather')
def weather_download(request, slug):
    obj = get_object_or_404(Weather, slug=slug)
    default_name = 'wthr'
    full_filename = obj.filename()
    filename = full_filename[:-4]
    context = {
        'show_help': True,
        'wthr': obj,
        'filename': filename,
        'wksname': 'wthr',
    }

    if request.method == 'POST':
        # POST
        src = (settings.MEDIA_ROOT + '/' + obj.weatherfile.name).replace('\\', '/')
        if 'txt' in request.POST:
            return download(src, full_filename)
        else:
            loc = src.rfind('/')
            path = src[:loc]
            token_value = request.POST.get('token_value')
            if 'update_xl' in request.POST:
                return update_xl(request, context, path, src, default_name, token_value)
            else:
                name = '{0}.xlsx'.format(filename)
                xlname = path + '/' + name
                Export2XL(src, xlname, default_name).create_xl()
                xlsrc = xlname
                return download_xl(xlsrc, name, token_value)
    else:
        # GET
        return render(request, 'weather/weather_download.html', context)


def download(src, filename):
    wrapper = FileWrapper(open(src, 'r'))
    response = HttpResponse(wrapper, content_type='application/octet-stream')
    response['Content-Length'] = os.path.getsize(src)
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


@require_authenticated_permission('weather.add_weather')
def update_xl(request, context, path, src, sheet_name, token_value):
    template_file = 'weather/weather_download.html'
    err_icon = '<i class="fas fa-times"></i> {0}'
    myfile = request.FILES.getlist('myfile')

    if not myfile:
        msg = err_icon.format('No Excel file specified.')
        messages.add_message(request, settings.PYSW_ERROR, msg)
        context['show_help'] = ''
        return render(request, template_file, context)

    fs = FileSystemStorage(location=path)
    filename = path + '/' + fs.save(myfile[0].name, myfile[0])

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
