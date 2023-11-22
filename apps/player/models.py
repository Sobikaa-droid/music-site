from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.core.files.storage import default_storage
from functools import partial
import os


def delete_file(instance, field):
    field_value = getattr(instance, field, None)

    # Check if the field value is not None and the file exists
    if field_value and default_storage.exists(field_value.path):
        default_storage.delete(field_value.path)


def get_upload_path(instance, filename, folder_type):
    first_letter = instance.title[0].capitalize()
    if first_letter not in list('1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        first_letter = '$'
    folder_path = f"{folder_type}s/{first_letter}/"
    return os.path.join(folder_path, filename)


get_upload_path_song = partial(get_upload_path, folder_type="song")
get_upload_path_album = partial(get_upload_path, folder_type="album")
get_upload_path_playlist = partial(get_upload_path, folder_type="playlist")


class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_path_song)
    audio_file = models.FileField(upload_to=get_upload_path_song, blank=True, null=True)
    audio_link = models.CharField(max_length=400, blank=True, null=True)
    slug_artist = models.SlugField(blank=True, null=True)
    slug_song = models.SlugField(blank=True, null=True)

    class Meta:
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(fields=['title', 'artist'], name='unique_song_title_per_user')
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if not self.audio_file and not self.audio_link:
            raise ValidationError("Either audio file or audio link must be provided.")

    def save(self, *args, **kwargs):
        self.clean()
        # Delete the old image or audio file if a new one is being uploaded
        if self.pk:
            old_instance = Song.objects.get(pk=self.pk)
            if self.image != old_instance.image:
                delete_file(old_instance, 'image')
            if self.audio_file != old_instance.audio_file:
                delete_file(old_instance, 'audio_file')

        # Generate slug fields
        self.slug_artist = slugify(str(self.artist))
        self.slug_song = slugify(str(self.title))

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_file(self, 'image')
        delete_file(self, 'audio_file')
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('player:song', args=[self.slug_artist, self.slug_song])


class SavedSong(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='saved_song_set')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_artist_set')

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f"{self.user}: {self.song}"


class AlbumType(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000, null=True, blank=True)
    image = models.ImageField(upload_to=get_upload_path_album)
    songs = models.ManyToManyField(Song)
    type = models.ForeignKey(AlbumType, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    slug_artist = models.SlugField(blank=True, null=True)
    slug_album = models.SlugField(blank=True, null=True)

    class Meta:
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(fields=['title', 'artist'], name='unique_album_title_per_user')
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Delete the old image if a new one is being uploaded
        if self.pk:
            old_instance = Album.objects.get(pk=self.pk)
            if old_instance.image != self.image:
                delete_file(old_instance, 'image')

        # Generate slug fields
        self.slug_artist = slugify(self.artist)
        self.slug_album = slugify(self.title)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_file(self, 'image')
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('player:album', args=[self.slug_artist, self.slug_album])


class Playlist(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True, blank=True)
    image = models.ImageField(upload_to=get_upload_path_playlist, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    songs = models.ManyToManyField(SavedSong, blank=True)
    slug = models.SlugField(blank=True, null=True)

    class Meta:
        ordering = ['last_update_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.clean()
        # Delete the old image or audio file if a new one is being uploaded
        if self.pk:
            old_instance = Playlist.objects.get(pk=self.pk)
            if old_instance.image and self.image != old_instance.image:
                delete_file(old_instance, 'image')

        # Generate slug fields
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_file(self, 'image')

    def get_absolute_url(self):
        return reverse('player:playlist', args=[str(self.pk), self.slug])
