import os
import tempfile

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File

from organizer.delete_file import delete_file
from .models import Weather


class WeatherForm(forms.ModelForm):
    class Meta:
        model = Weather
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.upload_errors = 0
        super(WeatherForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        obj = super(WeatherForm, self).save(*args, **kwargs)
        if self.request:
            obj.owner = self.request.user
        obj.save()
        return obj

    def getfilepath(self, fname):
        filename = ''
        if fname:
            real_fname = fname.replace(' ', '_')
            filename = '{0}/user_{1}/weather/{2}'.format(settings.MEDIA_ROOT,
                                                         self.request.user.id, real_fname)
        return filename

    def clean(self):
        def upload_file(source_filename, source_path, replace_filename=None):
            filename = replace_filename if replace_filename else source_filename.replace(' ', '_')
            upload_path = self.getfilepath(filename)
            path = os.path.join(settings.MEDIA_ROOT, source_path)
            source_filepath = path + source_filename

            if os.path.isfile(upload_path):
                msg = '"{0}" already exists!'.format(filename)
                if replace_filename:
                    delete_file(source_filepath)
                raise ValidationError(msg)

            tf = tempfile.NamedTemporaryFile()
            with open(source_filepath, 'rb') as fin:
                tf.write(fin.read())
            tf.seek(0)
            django_file = File(tf)
            model_instance = self.save(commit=False)
            model_instance.weatherfile.save(filename, django_file, save=True)
            if replace_filename:
                delete_file(source_filepath)

        cleaned_data = super(WeatherForm, self).clean()

        wthrfile = cleaned_data['weatherfile']
        if wthrfile:
            wfname = wthrfile.name
            wfsize = wthrfile.size
            to_fullpath = self.getfilepath(wfname)
            if os.path.isfile(to_fullpath):
                msg = '"{0}" already exists! Please choose another file.'.format(wfname)
                raise ValidationError(msg)
            elif wfsize > 1 * 1024 * 1024:
                msg = '"{0}" is too large ({1:.1f} Mb)! File size must be 1 Mb or smaller.'
                raise ValidationError(msg.format(wfname, wfsize / (1024 * 1024)))

        repofile = cleaned_data['repofile']
        nasafile = cleaned_data['nasafile']
        if not wthrfile and not repofile and not nasafile:
            raise ValidationError('Please specify a weather file to upload.')

        if repofile:
            upload_file(repofile, 'repository/weather/')
        elif nasafile:
            nasa_tfile = cleaned_data['nasa_tfile']
            upload_file(nasa_tfile, 'nasa/', nasafile)

        return cleaned_data
