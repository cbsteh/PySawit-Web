import logging
import os
from io import BytesIO

from PIL import Image
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from organizer.delete_file import delete_file
from .models import UserProfile
from .utils import ActivationMailFormMixin

logger = logging.getLogger(__name__)


class ResendActivationEmailForm(ActivationMailFormMixin, forms.Form):
    email = forms.EmailField()
    mail_validation_error = ('Could not re-send activation email. '
                             'Please try again later. (Sorry!)')

    def save(self, **kwargs):
        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(email=self.cleaned_data['email'])
        except:
            email = self.cleaned_data['email']
            logger.warning('Resend Activation: No user with email: {}.'.format(email))
            return None
        self.send_mail(user=user, **kwargs)
        return user

    def send_mail(self, user, **kwargs):
        sent, err = super(ResendActivationEmailForm, self).send_mail(user, **kwargs)
        if not sent:
            self.add_error(
                None,  # no field - form error
                ValidationError(self.mail_validation_error, code=err))
        return sent


class UserCreationForm(ActivationMailFormMixin, BaseUserCreationForm):
    mail_validation_error = ('User created. Could not send activation email. '
                             'Please try again later. (Sorry!)')

    class Meta(BaseUserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, **kwargs):
        user = super().save(commit=False)
        if not user.pk:
            user.is_active = False
            send_mail = True
        else:
            send_mail = False
        user.save()
        self.save_m2m()
        if send_mail:
            self.send_mail(user=user, **kwargs)

        # by default, the new user belongs to the Normal group
        normal_group = Group.objects.get(name='Normal')
        normal_group.user_set.add(user)
        return user

    def send_mail(self, user, **kwargs):
        sent, err = super(UserCreationForm, self).send_mail(user, **kwargs)
        if not sent:
            self.add_error(
                None,  # no field - form error
                ValidationError(self.mail_validation_error, code=err))
        return sent


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


def get_resize_image_size(image):
    max_w, max_h = 200, 200
    img_w, img_h = image.size
    if img_h > img_w:
        ratio = max_h / img_h
        new_w = int(img_w * ratio)
        new_h = max_h
    else:
        ratio = max_w / img_w
        new_h = int(img_h * ratio)
        new_w = max_w
    return new_w, new_h


def resize_image(img):
    size = get_resize_image_size(img)
    img = img.resize(size, Image.ANTIALIAS)
    return img


def process_django_file(pil_image, name, fmt='png'):
    """
    Process the PIL file to Django File
    """
    file_object = BytesIO()
    pil_image.save(file_object, format=fmt)
    content = file_object.getvalue()
    return ContentFile(content, name=name)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', ]

    avatar_fname = 'avatar.png'
    avatar_img_type = 'png'
    avatar_path = 'user_{}/avatar/{}'

    remove_avatar = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)

    def getfullpath(self):
        path = self.avatar_path.format(self.user.id, self.avatar_fname)
        filename = '{}/{}'.format(settings.MEDIA_ROOT, path)
        return filename

    def clean(self):
        cleaned_data = super(UserProfileForm, self).clean()
        # extended user profile can be null (not instantiated)
        if cleaned_data:
            avatar = cleaned_data['avatar']
            # check if profile picture has been set/instantiated
            if avatar:
                # check if remove_avatar info is sent and true
                if 'remove_avatar' in cleaned_data and cleaned_data['remove_avatar']:
                    avatar.delete(save=True)
                else:
                    path = self.avatar_path.format(self.user.id, self.avatar_fname)
                    # check if new avatar photo specified
                    if avatar.name.lower() != path:
                        fullfilepath = self.getfullpath()
                        if os.path.isfile(fullfilepath):
                            delete_file(fullfilepath)   # clean up; ensure one user, one file
                            if os.path.isfile(fullfilepath):
                                # for some reason, cannot delete old avatar photo file, so abort
                                msg = 'Error uploading your profile photo. Please try again later.'
                                raise ValidationError(msg)
                        # resize new avatar photo and convert to to img_type image type
                        pil_image = Image.open(avatar)
                        pil_image = resize_image(pil_image)
                        avatar.file = process_django_file(pil_image,
                                                          name=self.avatar_fname,
                                                          fmt=self.avatar_img_type)
                        avatar.name = self.avatar_fname
                        avatar.content_type = 'image/{0}'.format(self.avatar_img_type)

        return cleaned_data
