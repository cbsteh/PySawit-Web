from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.views.defaults import page_not_found as default_page_not_found
from django.views.defaults import server_error as default_server_error

from markdown import markdown
from collections import OrderedDict


def redirect_root(request):
    return title(request)


def title(request):
    return render(request, 'title/title.html', {})


def about(request):
    return render(request, 'help/about/about.html', {})


def privacy_policy(request):
    return render(request, 'help/about/privacy_policy.html', {})


def credits(request):
    return render(request, 'help/about/credits.html', {})


def pysawit_report(request):
    pdffile = '{0}/repository/docs/{1}'.format(settings.MEDIA_ROOT, 'pysawit-report.pdf')
    return FileResponse(open(pdffile, 'rb'), content_type='application/pdf')


def op_chapter(request):
    pdffile = '{0}/repository/docs/{1}'.format(settings.MEDIA_ROOT, 'op-chapter.pdf')
    return FileResponse(open(pdffile, 'rb'), content_type='application/pdf')


def op_article_jtas(request):
    pdffile = '{0}/repository/docs/{1}'.format(settings.MEDIA_ROOT, 'op-article-jtas.pdf')
    return FileResponse(open(pdffile, 'rb'), content_type='application/pdf')


# error pages:
def not_found(request, exception=None, template_name='organizer/errors/404.html'):
    return default_page_not_found(request, exception, template_name=template_name)


def server_error(request, template_name='organizer/errors/500.html'):
    return default_server_error(request, template_name=template_name)


# markdown cheat sheet
def md_cheatsheet(request):
    def replace_eol(txt):
        return txt.replace('\n', '<br>').replace('&#x20;', '&nbsp;')

    def replace_space(txt):
        return txt.replace('&#x20;', ' ')

    ext = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'mdx_del_ins',
        'mdx_subscript',
        'mdx_superscript',
    ]

    s_dict = OrderedDict([
        ('New line<br><i>(leave at least 1 blank line)</i>',
         'Line A\n\nLine B\n\nLine C'),

        ('<i>Remark: No blank line, no new line</i>',
         'These 3 parts\nwill still be\non the same line.'),

        ('Line break<br><i>(add 2 or more spaces at the end of the line)</i>',
         'Line A  \nLine B  \nLine C  '),

        ('Heading 1',
         '#Heading 1'),

        ('Heading 2',
         '##Heading 2'),

        ('Heading 3',
         '###Heading 3'),

        ('Bold',
         '**Bold text**'),

        ('Italic',
         '*Italic text*'),

        ('Underline',
         '++Underline text++'),

        ('Superscript',
         '2^3^ is 8\n\nE = mc^2^'),

        ('Subscript',
         'CO~2~ is carbon dioxide\n\nH~2~O~2~ is hydrogen peroxide'),

        ('Strikethrough',
         '~~Strikethrough text~~'),

        ('Quote',
         '>Quote'),

        ('Nested quotes',
         ('>First quote\n\n>'
          'May nest more than 1 level\n\n'
          '>>Nested quote'
          '\n\n>>Every additional \'>\' adds a level'
          '\n\n>More lines')),

        ('Ordered list<br><i>(no need to number each item in sequence)</i>',
         '1. First item\n1. Second item\n1. Third item'),

        ('Unordered list',
          '- First item\n- Second item\n- Third item'),
        ('Highlight<br><i>(backticks)</i>',
         '`Highlight text`'),

        ('Horizontal rule/line<br><i>(three dashes)</i>',
         '---'),

        ('Link',
         '[Click me](http://www.example.com)'),

        ('Table',
         ('| Col. 1 | Col. 2 | Col. 3 |\n'
          '|--------|--------|--------|\n'
          '| Text 1 | Text 3 | Text 5 |\n'
          '| Text 2 | Text 4 | Text 6 |')),

        ('Block quote<br><i>(triple backticks)</i>',
         '```\nLine 1\nLine 2\nLine 3\n```'),

        ('Block quote<br><i>(prefix each line with 4 spaces)</i>',
         '&#x20;&#x20;&#x20;&#x20;Line 1\n'
         '&#x20;&#x20;&#x20;&#x20;Line 2\n'
         '&#x20;&#x20;&#x20;&#x20;Line 3'),

        ('Footnote',
         'Link to a footnote. [^1]\n\n\n[^1]: This is the footnote.'),
    ])

    preview = [(k, [replace_eol(v),
                    markdown(replace_space(v), extensions=ext)]) for k, v in s_dict.items()]
    md_dict = OrderedDict()
    md_dict.update([(p[0], p[1]) for p in preview])
    return render(request, 'wiki/md_cheatsheet.html', {'md_dict': md_dict})


def md_preview(request):
    ext = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'mdx_del_ins',
        'mdx_subscript',
        'mdx_superscript',
    ]
    syntax = request.GET.get('syntax', '')
    data = {
        'preview': markdown(syntax, extensions=ext),
    }
    return JsonResponse(data)


def help(request):
    return render(request, 'help/help_overview.html', {})


def help_minreq(request):
    return render(request, 'help/help_minreq.html', {})


def help_overview(request):
    return render(request, 'help/help_overview.html', {})


def help_wthrrepo(request):
    return render(request, 'help/help_wthrrepo.html', {})


def help_wthrnasa(request):
    return render(request, 'help/help_wthrnasa.html', {})


def help_wthrformat(request):
    return render(request, 'help/help_wthrformat.html', {})


def help_wthrprepare(request):
    return render(request, 'help/help_wthrprepare.html', {})


def help_wthrupload(request):
    return render(request, 'help/help_wthrupload.html', {})


def help_wthrdownload(request):
    return render(request, 'help/help_wthrdownload.html', {})


def help_wthrimport(request):
    return render(request, 'help/help_wthrimport.html', {})


def help_wthredit(request):
    return render(request, 'help/help_wthredit.html', {})


def help_wthrdelete(request):
    return render(request, 'help/help_wthrdelete.html', {})


def help_wthrmod(request):
    return render(request, 'help/help_wthrmod.html', {})


def help_modelinput(request):
    return render(request, 'help/help_modelinput.html', {})


def help_modelrun(request):
    return render(request, 'help/help_modelrun.html', {})


def help_outputresults(request):
    return render(request, 'help/help_outputresults.html', {})


def help_outputdownload(request):
    return render(request, 'help/help_outputdownload.html', {})


def help_outputparam(request):
    return render(request, 'help/help_outputparam.html', {})


def help_register(request):
    return render(request, 'help/help_register.html', {})


def help_userprofile(request):
    return render(request, 'help/help_userprofile.html', {})


def help_docs(request):
    return render(request, 'help/help_docs.html', {})


def help_wikinavigate(request):
    return render(request, 'help/wiki/help_wikinavigate.html', {})


def help_wikichanges(request):
    return render(request, 'help/wiki/help_wikichanges.html', {})


def help_wikicreate(request):
    return render(request, 'help/wiki/help_wikicreate.html', {})


def help_wikiedit(request):
    return render(request, 'help/wiki/help_wikiedit.html', {})


def help_wikiimages(request):
    return render(request, 'help/wiki/help_wikiimages.html', {})


def help_wikimove(request):
    return render(request, 'help/wiki/help_wikimove.html', {})


def help_wikisettings(request):
    return render(request, 'help/wiki/help_wikisettings.html', {})
