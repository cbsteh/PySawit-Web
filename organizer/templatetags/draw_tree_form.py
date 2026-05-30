import collections

from django.template import Library


register = Library()


@register.simple_tag
def draw_tree_form(form, fsets, html=None):
    if not html and fsets:
        html = '<ul>'
    for fset in fsets:
        html += '<li>{0}'.format(fset[0])
        d = fset[1]
        for i, name in enumerate(d['fields']):
            if i == 0:
                html += '<ul>'
            if not (isinstance(name, collections.Sequence) and not isinstance(name, str)):
                group_str = form.fields[name].widget.attrs['group']
                cmd = 'open_panel(\'{0}\',\'label_{1}\');'.format(group_str, name)
                label = form.fields[name].label
                html += '<li><a href="#" onclick="{0}">{1}</a>'.format(cmd, label)
            else:
                html = draw_tree_form(form, name, html)
            html += '</li>'
        html += '</li></ul>'
    return html
