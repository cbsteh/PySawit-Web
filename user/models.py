from django.db import models
from django.contrib.auth.models import User


def user_avatar_path(instance, filename):
    # avatar files will be uploaded to MEDIA_ROOT/user_<id>/avatar/<filename>
    return 'user_{0}/avatar/{1}'.format(instance.user.id, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True,
                                related_name='profile')

    avatar = models.ImageField(upload_to=user_avatar_path,
                               blank=True,
                               help_text='Upload your profile photo',
                               verbose_name='Profile photo')
