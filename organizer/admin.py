import shutil

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from weather.models import Weather
from .models import OPD
from user.models import UserProfile


# Register your models here.

site.disable_action('delete_selected')


def delete_user(modeladmin, request, queryset):
    for user in queryset:
        directory = '{0}/user_{1}/'.format(settings.MEDIA_ROOT, user.id)
        shutil.rmtree(directory, ignore_errors=True)
        directory = '{0}/requests/user_{1}/'.format(settings.MEDIA_ROOT, user.id)
        shutil.rmtree(directory, ignore_errors=True)
        user.delete()


delete_user.short_description = 'Zap selected users'


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',
                  'groups',
                  'email',
                  'first_name',
                  'last_name',
                  )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError('Email cannot be blank')
        return email

    def clean_groups(self):
        groups = self.cleaned_data['groups']
        if not groups:
            raise ValidationError('User must belong to at least one group')
        return groups


class CustomUserAdmin(UserAdmin):
    add_form = UserCreateForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',
                       'groups',
                       'email',
                       'first_name',
                       'last_name',
                       'password1',
                       'password2',
                       )}
         ),
    )

    list_filter = UserAdmin.list_filter + ('groups__name',)
    list_display = ('username',
                    'id',
                    'full_name',
                    'id_number',
                    'email',
                    'is_active',
                    'custom_groups',
                    )
    actions = [delete_user]

    def id_number(self, x):
        return x.first_name

    def full_name(self, x):
        return x.last_name

    def custom_groups(self, obj):
        return ','.join([g.name for g in obj.groups.all()]) if obj.groups.count() else ''

    def has_delete_permission(self, request, obj=None):
        return False


class OPDAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'owner_id']

    def owner_id(self, x):
        return x.owner.id


class WeatherAdmin(admin.ModelAdmin):
    list_display = ['description', 'weatherfile', 'owner', 'owner_id']

    def owner_id(self, x):
        return x.owner.id


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['profile_username', 'profile_id', 'has_photo', 'avatar']

    def profile_username(self, x):
        return x.user.username

    def profile_id(self, x):
        return x.user.id

    def has_photo(self, x):
        return True if x.avatar else False


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(OPD, OPDAdmin)
admin.site.register(Weather, WeatherAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.site_header = 'PySawit Web'
admin.site.site_title = 'PySawit Web'
