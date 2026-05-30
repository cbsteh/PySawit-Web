from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator

from user.decorators import require_authenticated_permission


class ObjectMixin:
    form_class = None
    model = None
    template_name = ''
    exit_url = ''


class ObjectCreateMixin(ObjectMixin):
    create_url = ''

    @method_decorator(require_authenticated_permission('organizer.add_opd'))
    def get(self, request):
        context = {
            'header': '(New)',
            'form': self.form_class(request.user),
            'form_action': self.create_url,
            'form_disabled': False,
            'form_create': True,
        }
        return render(request, self.template_name, context)

    @method_decorator(require_authenticated_permission('organizer.add_opd'))
    def post(self, request):
        if 'cancel' in request.POST:
            return redirect(self.exit_url)

        bound_form = self.form_class(request.user, request.POST)
        if bound_form.is_valid():
            new_object = bound_form.save()
            if 'run' in request.POST:
                return redirect(new_object.get_confirm_run_url())
            msg = '<i class="fas fa-check"></i> "{}" successfully saved.'
            messages.add_message(request, settings.PYSW_SUCCESS, msg.format(new_object.name))
            return redirect(new_object.get_update_url())
        else:
            context = {
                'header': '(New)',
                'form': bound_form,
                'form_action': self.create_url,
                'form_disabled': False,
                'form_create': True,
            }
            return render(request, self.template_name, context)


class ObjectUpdateMixin(ObjectMixin):
    @method_decorator(require_authenticated_permission('organizer.change_opd'))
    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug=slug)
        context = {
            'header': '(Edit) ' + obj.name,
            'has_request': obj.has_request(),
            'form': self.form_class(request.user, instance=obj),
            'form_action': obj.get_update_url,
            'form_disabled': False,
            'form_create': False,
        }
        return render(request, self.template_name, context)

    @method_decorator(require_authenticated_permission('organizer.change_opd'))
    def post(self, request, slug):
        if 'cancel' in request.POST:
            return redirect(self.exit_url)

        obj = get_object_or_404(self.model, slug=slug)
        bound_form = self.form_class(request.user, request.POST, instance=obj)
        if bound_form.is_valid():
            new_object = bound_form.save()
            if 'run' in request.POST:
                return redirect(new_object.get_confirm_run_url())
            msg = '<i class="fas fa-check"></i> "{}" successfully saved.'
            messages.add_message(request, settings.PYSW_SUCCESS, msg.format(new_object.name))
            return redirect(new_object.get_update_url())
        else:
            context = {
                'header': '(Edit) ' + obj.name,
                'has_request': obj.has_request(),
                'form': bound_form,
                'form_action': obj.get_update_url,
                'form_disabled': False,
                'form_create': False,
            }
            return render(request, self.template_name, context)


class ObjectDetailMixin(ObjectUpdateMixin):
    @method_decorator(require_authenticated_permission('organizer.change_opd'))
    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug=slug)
        formobj = self.form_class(request.user, instance=obj)
        formobj.disabled = True
        context = {
            'header': obj.name,
            'has_request': obj.has_request(),
            'form': formobj,
            'form_action': obj.get_absolute_url,
            'form_disabled': True,
            'form_create': False,
        }
        return render(request, self.template_name, context)

    @method_decorator(require_authenticated_permission('organizer.change_opd'))
    def post(self, request, slug):
        if 'cancel' in request.POST:
            return redirect(self.exit_url)

        obj = get_object_or_404(self.model, slug=slug)
        if 'run' in request.POST:
            return redirect(obj.get_confirm_run_url())
        return redirect(obj.get_update_url())
