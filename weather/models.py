import re
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from weather.charts import WeatherStats


def output_as_table(filename):
    html = '<thead>'
    bfound_header = False
    tag1, tag2 = '<th>', '</th>'
    with open(filename, 'r') as fp:
        n = 0
        for txtline in fp:
            if txtline.lstrip(' ')[0] == '#':
                continue

            html += '<tr>'
            txtlst = [txt for txt in txtline.split(',') if txt.strip()]
            for i, txt in enumerate(txtlst):
                if not bfound_header:
                    # doing table headers:
                    txt = txt.replace('_', '_<br/>').replace('*', '')
                    if i == 0:
                        txt = 'year: ' + txt
                else:
                    # doing table data:
                    if i == 0:
                        yearno = int(n / 365) + 1
                        txt = str(yearno) + ': ' + txt
                        n += 1

                cleantxt = txt.strip(' ')
                html += tag1 + cleantxt + tag2
            html += '</tr>'

            if not bfound_header:
                bfound_header = True
                tag1, tag2 = '<td>', '</td>'
                html += '</thead><tbody>'

    if bfound_header:
        html += '</tbody>'
    return html


def user_folder_path(instance, filename):
    # weather files will be uploaded to MEDIA_ROOT/user_<id>/weather/<filename>
    return 'user_{0}/weather/{1}'.format(instance.owner.id, filename)


class Weather(models.Model):
    class Meta:
        ordering = ['weatherfile']

    owner = models.ForeignKey(User,
                              blank=True,
                              null=True,
                              on_delete=models.CASCADE)

    slug = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    description = models.CharField(max_length=255,
                                   blank=True,
                                   help_text='Brief description of this weather file',
                                   verbose_name='Description')

    weatherfile = models.FileField(upload_to=user_folder_path,
                                   blank=True,
                                   help_text='Name of weather file to use',
                                   verbose_name='Weather file')

    repofile = models.CharField(max_length=255, blank=True)

    nasafile = models.CharField(max_length=255, blank=True)

    nasa_tfile = models.CharField(max_length=255, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename()

    def filename(self):
        pos = self.weatherfile.name.rfind('/')
        return self.weatherfile.name[pos+1:]

    @property
    def name(self):
        return self.filename()

    def has_request(self):
        return False

    def display_weather(self):
        textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
        is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
        if is_binary_string(open(self.weatherfile.path, 'rb').read(1024)):
            msg = 'This file is likely not a weather file (or is incorrectly formatted). '
            msg += 'Please delete this file and reupload.'
            return [False, msg, [], []]

        html = ('<div class="tableFixHead">'
                '<table>{0}</table></div>').format(output_as_table(self.weatherfile.path))
        try:
            charts, stats = self.get_charts()
        except ValueError as e:
            return [False, e, [], []]

        return [True, html, charts, stats]

    def get_charts(self):
        ws = WeatherStats(self.weatherfile.path)
        WeatherStats.set_plot()
        ws.plot_scatter('tmin', 'tmin ($^\circ$C)', 'Min. air temperature')
        ws.plot_histogram('tmin', 'tmin ($^\circ$C)', 'Distribution of min. air temperature')

        ws.plot_scatter('tmax', 'tmax ($^\circ$C)', 'Max. air temperature')
        ws.plot_histogram('tmax', 'tmax ($^\circ$C)', 'Distribution of max. air temperature')

        ws.plot_scatter('wind', 'wind (m s$^{-1}$)',  'Wind speed')
        ws.plot_histogram('wind', 'wind (m s$^{-1}$)', 'Distribution of wind speed')

        ws.plot_scatter('rain', 'rain (mm)', 'Rain')
        ws.plot_histogram('rain', 'rain (mm)', 'Distribution of rain')

        ws.plot_scatter_avg('tmin', 'tmin ($^\circ$C)', 'Annual mean min. air temperature')
        ws.plot_scatter_avg('tmax', 'tmax ($^\circ$C)', 'Annual mean max. air temperature')
        ws.plot_scatter_avg('wind', 'wind (m s$^{-1}$)', 'Annual mean wind speed', True)
        ws.plot_scatter_sum('rain', 'rain (mm)', 'Annual total rain', True)

        ws.stats_min_air_temp()
        ws.stats_max_air_temp()
        ws.stats_wind()
        ws.stats_rain()
        return ws.figures, ws.stats

    def get_absolute_url(self):
        return reverse('weather_detail', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('weather_delete', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('weather_update', kwargs={'slug': self.slug})

    def get_download_url(self):
        return reverse('weather_download', kwargs={'slug': self.slug})
