import collections

from django.template import Library


register = Library()


class Flag:
    def __init__(self):
        self.level = 0
        self.valid = True
        self.fields = ''


@register.simple_tag
def draw_form(form, fieldsets=None, disabled=False, flag=None):
    def is_sequence(obj):
        return isinstance(obj, collections.Sequence) and not isinstance(obj, str)

    def get_fields_html(in_form, in_fields, in_flag):
        taglist = ['<input', '<textarea', '<select']
        panel_start = '<table class="table table-condensed"><tbody>'
        panel_end = '</tbody></table>'
        fields_html = []
        append = fields_html.append
        append(panel_start)

        for field_name in in_fields:
            if is_sequence(field_name):
                bvalid = in_flag.valid
                in_flag.valid = True
                in_flag.level += 1
                field_name = draw_form(in_form, field_name, disabled, in_flag)
                in_flag.level -= 1
                if in_flag.valid and bvalid:
                    in_flag.valid = True
                else:
                    in_flag.valid = False
                append(panel_end + field_name)
            else:
                field = in_form[field_name]
                txtfield = str(field)
                if disabled:
                    for tag in taglist:
                        txt = txtfield.replace(tag, tag + ' disabled')
                        txtfield = txt
                cls = []
                help_text0 = help_text1 = ''
                errors = ''
                if in_form.fields[field_name].required:
                    cls.append('required')
                if field.help_text:
                    top = field.help_text[0]
                    if top == '^':
                        help_text0 = '{0}<br/>'.format(field.help_text[1:])
                        help_text1 = ''
                    else:
                        help_text0 = ''
                        help_text1 = '<br/>{0}'.format(field.help_text)

                if in_form[field_name].errors:
                    in_flag.valid = False
                    errors = str(in_form[field_name].errors)
                    cls.append('error')
                cls = ' class="{0}"'.format(" ".join(cls))
                line = ('<tr>'
                            '<td{cl}>'
                                '<span class="anchor" id="label_{fn}"></span>'
                                '<label for="{fn}">{fl}</label>'
                            '</td>'
                            '<td>'
                                '{er}'
                                '{ht0}'
                                '{fi}'
                                '{ht1}'
                                '<span id="msg_{fn}" style="font-style:italic;"></span>'
                            '</td>'
                        '</tr>')
                append(line.format(cl=cls,
                                   fn=field_name,
                                   fl=field.label,
                                   er=errors,
                                   ht0=help_text0,
                                   ht1=help_text1,
                                   fi=txtfield))

        in_flag.fields = ''.join(fields_html) + panel_end
        return in_flag

    if flag is None:
        flag = Flag()

    form_html = []
    append_to_form = form_html.append
    form.auto_id = True

    fieldset_template = (
        '<div class="panel panel-default">'
            '<div class="panel-heading"%(style)s>'
                '<h4 class="panel-title">'
                    '<a data-toggle="collapse" href="#%(id)s" tabindex="-1">'
                    '<i class="fas fa-list-ul"></i></a> '
                    '<a data-toggle="collapse" href="#%(id)s" tabindex="-1">%(legend)s</a>'
                    '<span style="float:right;cursor:pointer;">'
                        '<span rel="tooltip" title="Toggle tree view" class="toggle-sidenav">'
                            '<i class="fas fa-toggle-off sidenav-icon" style="color:orange;"></i> '
                        '</span>'
                    '</span>'
                '</h4>'
            '</div>'
            '<div id="%(id)s" class="panel-collapse collapse%(error)s">'
                '<div class="panel-body">'
                    '%(fields)s'
                '</div>'
            '</div>'
        '</div>'
    )

    color = ['#fff8de', '#f6ffde', '#ffe8de']
    if fieldsets:
        for i, fieldset in enumerate(fieldsets):
            context = {}
            dct = fieldset[1]
            id = dct.get('id')

            if id:
                context['id'] = id
            else:
                context['id'] = ''

            if flag.level == 0:
                flag.valid = True

            context['legend'] = fieldset[0]
            fields = dct['fields']
            flag = get_fields_html(form, fields, flag)
            context['fields'] = flag.fields
            context['style'] = 'style="background:{0};"'.format(color[flag.level % len(color)])

            if disabled:
                context['default'] = 'Edit'
                context['default_icon'] = 'far fa-edit'
            else:
                context['default'] = 'Save'
                context['default_icon'] = 'far fa-save'

            if not flag.valid or (i == 0 and flag.level == 0 and not form.errors):
                context['error'] = ' in'
            else:
                context['error'] = ''

            append_to_form(fieldset_template % context)

        return ''.join(form_html)
    else:
        fields = form.fields.keys()
        return get_fields_html(form, fields, flag)
