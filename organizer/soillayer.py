from django import forms
from django.db import models


class SoilLayerWidget(forms.MultiWidget):
    template_name = 'widgets/multiwidget_soillayer.html'

    def __init__(self, *args, **kwargs):
        attrs = {'size': '6'}
        widgets = (forms.TextInput(attrs),
                   forms.TextInput(attrs),
                   forms.TextInput(attrs),
                   forms.TextInput(attrs),
                   forms.TextInput(attrs),
                   )
        widgets[0].attrs['label'] = 'Layer thickness'
        widgets[0].attrs['help_text'] = '(m): Thickness of soil layer'
        widgets[1].attrs['label'] = 'Initial water content'
        widgets[1].attrs['help_text'] = ('(m3/m3): Vol. soil water content. '
                                         'Or enter -1, -2, or -3 for saturation, '
                                         'field capacity, or permanent wilting '
                                         'point, respectively')
        widgets[2].attrs['label'] = 'Clay'
        widgets[2].attrs['help_text'] = '(%): Clay content'
        widgets[3].attrs['label'] = 'Sand'
        widgets[3].attrs['help_text'] = '(%): Sand content'
        widgets[4].attrs['label'] = 'OM'
        widgets[4].attrs['help_text'] = '(%): Organic matter (OM) content'
        super(SoilLayerWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value:
            return value.split(',')
        return ''

    def highlight_field(self, idx, highlight):
        if highlight:
            self.widgets[idx].attrs.update({'style': 'border-color: red'})
        else:
            self.widgets[idx].attrs.pop('style', None)


class SoilLayerField(forms.MultiValueField):
    widget = SoilLayerWidget

    def __init__(self, *args, **kwargs):
        fields = (forms.CharField(),
                  forms.CharField(),
                  forms.CharField(),
                  forms.CharField(),
                  forms.CharField(),)
        super(SoilLayerField, self).__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return ''


class SoilLayerModelField(models.Field):
    def formfield(self, **kwargs):
        defaults = {'form_class': SoilLayerField}
        defaults.update(kwargs)
        return super(SoilLayerModelField, self).formfield(**defaults)

    def db_type(self, connection):
        return 'array'
