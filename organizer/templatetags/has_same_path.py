from django.template import Library


register = Library()


@register.filter
def has_same_path(article_path, request_path):
    tokens = ['/_edit/', '/_history/', '/_plugin/', '/_settings/', '/_move/']
    pos = -1
    for token in tokens:
        pos = request_path.rfind(token)
        if pos >= 0:
            break

    if pos >= 0:
        request_path = request_path[:pos+1]

    return article_path == request_path
