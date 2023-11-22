from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse
from django.core.files.storage import default_storage
import os

# def delete_folder(instance):
#     folder_path = os.path.join(settings.MEDIA_ROOT, instance.folder_path)
#     if os.path.exists(folder_path):
#         shutil.rmtree(folder_path, ignore_errors=True)


# def get_upload_path(instance, filename):
#     """Get or Create upload path for model field."""
#     if instance.pk:
#         return os.path.join(instance.folder_path, filename)
#     else:
#         folder_name = f"users/user_{uuid.uuid4()}/"
#         instance.folder_path = folder_name
#         return os.path.join(folder_name, filename)

def delete_file(instance, field):
    field_value = getattr(instance, field, None)

    # Check if the field value is not None and the file exists
    if field_value and default_storage.exists(field_value.path):
        default_storage.delete(field_value.path)


def get_upload_path(instance, filename):
    first_letter = instance.username[0].capitalize()
    if first_letter not in list('1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        first_letter = '$'
    folder_path = f"users/{first_letter}/"
    return os.path.join(folder_path, filename)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    description = models.TextField(max_length=1500, null=True, blank=True)
    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    verified = models.BooleanField(default=False)
    slug = models.SlugField(blank=True, null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Delete the old image if a new one is being uploaded
        if self.pk:
            old_instance = CustomUser.objects.get(pk=self.pk)
            if self.image != old_instance.image:
                delete_file(old_instance, 'image')

        # Generate slug fields
        self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_file(self, 'image')
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('users:user', args=[self.slug])
