from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Song, Album, Playlist


class SongForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput)
    audio_file = forms.FileField(widget=forms.FileInput, required=False)

    class Meta:
        model = Song
        fields = ['title', 'image', 'audio_file', 'audio_link']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        self.fields['audio_link'].help_text = 'Link should end with ".mp3"'

    def clean_title(self):
        title = self.cleaned_data.get('title')
        qs = Song.objects.filter(title=title, artist=self.user)
        if qs.exists() and qs.first().pk != self.instance.pk:
            raise ValidationError("You already have a song with this title.")
        return title


class AlbumForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Album
        fields = ['title', 'image', 'description', 'songs', 'type']

    def __init__(self, *args, **kwargs,):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

        self.fields['songs'].help_text = 'You can only choose your own songs.'

    def clean_title(self):
        title = self.cleaned_data.get('title')
        qs = Album.objects.filter(title=title, artist=self.user)
        if qs.exists() and qs.first().pk != self.instance.pk:
            raise ValidationError("You already have an album with this title.")
        return title


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'image', 'description', 'songs']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

        self.fields['songs'].help_text = 'You can only choose songs you saved.'
