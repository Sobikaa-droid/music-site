from django.contrib import admin
from . import models

admin.site.register([
    models.AlbumType,
    models.Album,
    models.Playlist,
    models.Song,
    models.SavedSong,
])
