from django import forms
from django.db import models


class Array2DWidget(forms.MultiWidget):
    template_name = 'widgets/multiwidget.html'
    template_name_text = 'widgets/text.html'

    def __init__(self, widgets, attrs=None):
        super(Array2DWidget, self).__init__(widgets, attrs)
        if len(self.widgets) > 1:
            self.widgets[0].attrs['readonly'] = True
            self.widgets[1].attrs['readonly'] = True
            self.widgets[0].attrs['tabindex'] = '-1'
            self.widgets[1].attrs['tabindex'] = '-1'
            self.widgets[0].template_name = self.template_name_text
            self.widgets[1].template_name = self.template_name_text
        else:
            raise IndexError('At least two widgets are required.')

    def decompress(self, value):
        if value:
            return value.split(',')
        return ['', '']

    def highlight_field(self, idx, highlight):
        if highlight:
            self.widgets[idx].attrs = {'style': 'border-color: red'}
        else:
            self.widgets[idx].attrs.pop('style', None)


class Array2DField(forms.MultiValueField):
    def __init__(self, fields, *args, **kwargs):
        super(Array2DField, self).__init__(fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return ''


class Array12Widget(Array2DWidget):
    def __init__(self, attrs=None):
        attrs = {'size': '6'}
        widgets = (forms.TextInput(attrs), forms.TextInput(attrs),  # 1 (headers)
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 2
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 3
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 4
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 5
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 6
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 7
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 8
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 9
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 10
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 11
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 12
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 13
                   )
        super(Array12Widget, self).__init__(widgets, attrs)


class Array12Field(Array2DField):
    widget = Array12Widget

    def __init__(self, *args, **kwargs):
        fields = (forms.CharField(), forms.CharField(),  # 1 (headers)
                  forms.CharField(), forms.CharField(),  # 2
                  forms.CharField(), forms.CharField(),  # 3
                  forms.CharField(), forms.CharField(),  # 4
                  forms.CharField(), forms.CharField(),  # 5
                  forms.CharField(), forms.CharField(),  # 6
                  forms.CharField(), forms.CharField(),  # 7
                  forms.CharField(), forms.CharField(),  # 8
                  forms.CharField(), forms.CharField(),  # 9
                  forms.CharField(), forms.CharField(),  # 10
                  forms.CharField(), forms.CharField(),  # 11
                  forms.CharField(), forms.CharField(),  # 12
                  forms.CharField(), forms.CharField(),  # 13
                  )
        super(Array12Field, self).__init__(fields=fields, *args, **kwargs)


class Array16Widget(Array2DWidget):
    def __init__(self, attrs=None):
        attrs = {'size': '6'}
        widgets = (forms.TextInput(attrs), forms.TextInput(attrs),  # 1 (headers)
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 2
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 3
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 4
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 5
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 6
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 7
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 8
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 9
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 10
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 11
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 12
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 13
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 14
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 15
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 16
                   forms.TextInput(attrs), forms.TextInput(attrs),  # 17
                   )
        super(Array16Widget, self).__init__(widgets, attrs)


class Array16Field(Array2DField):
    widget = Array16Widget

    def __init__(self, *args, **kwargs):
        fields = (forms.CharField(), forms.CharField(),  # 1 (headers)
                  forms.CharField(), forms.CharField(),  # 2
                  forms.CharField(), forms.CharField(),  # 3
                  forms.CharField(), forms.CharField(),  # 4
                  forms.CharField(), forms.CharField(),  # 5
                  forms.CharField(), forms.CharField(),  # 6
                  forms.CharField(), forms.CharField(),  # 7
                  forms.CharField(), forms.CharField(),  # 8
                  forms.CharField(), forms.CharField(),  # 9
                  forms.CharField(), forms.CharField(),  # 10
                  forms.CharField(), forms.CharField(),  # 11
                  forms.CharField(), forms.CharField(),  # 12
                  forms.CharField(), forms.CharField(),  # 13
                  forms.CharField(), forms.CharField(),  # 14
                  forms.CharField(), forms.CharField(),  # 15
                  forms.CharField(), forms.CharField(),  # 16
                  forms.CharField(), forms.CharField(),  # 17
                  )
        super(Array16Field, self).__init__(fields=fields, *args, **kwargs)


class Array12ModelField(models.Field):
    def formfield(self, **kwargs):
        defaults = {'form_class': Array12Field}
        defaults.update(kwargs)
        return super(Array12ModelField, self).formfield(**defaults)

    def db_type(self, connection):
        return 'array'

class Array16ModelField(models.Field):
    def formfield(self, **kwargs):
        defaults = {'form_class': Array16Field}
        defaults.update(kwargs)
        return super(Array16ModelField, self).formfield(**defaults)

    def db_type(self, connection):
        return 'array'
