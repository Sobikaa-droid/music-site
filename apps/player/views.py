from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.conf import settings

from .models import Album, Playlist, Song, SavedSong
from .forms import SongForm, AlbumForm, PlaylistForm


class SongsListView(generic.ListView):
    model = Song
    context_object_name = 'songs'
    paginate_by = 10
    template_name = "player/songs_list.html"

    def get_queryset(self):
        qs = super().get_queryset().select_related('artist')
        search_val = self.request.GET.get('search_val', None)
        order_val = self.request.GET.get('order_by', '-pk')
        user = self.request.user
        if search_val:
            qs = qs.filter(title__icontains=search_val)
        qs = qs.order_by(order_val)

        # Annotate an additional field 'is_saved' to each song object
        if user.is_authenticated:
            qs = qs.annotate(is_saved=Exists(SavedSong.objects.filter(song=OuterRef('pk'), user=user)))

        return qs


class SongCreateView(generic.CreateView):
    form_class = SongForm
    template_name = 'player/object_create_base.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})

        return kwargs

    def form_valid(self, form):
        form.instance.artist = self.request.user
        messages.success(self.request, f'Song ({form.instance.title}) has been uploaded.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'Song'

        return context

    def get_success_url(self):
        return self.object.get_absolute_url()


class SongDetailView(generic.DetailView):
    model = Song
    context_object_name = 'song'
    template_name = 'player/song.html'

    def get_object(self, queryset=None):
        slug_artist = self.kwargs.get('slug_artist')
        slug_song = self.kwargs.get('slug_song')
        song_object = Song.objects.select_related('artist').get(slug_song=slug_song, slug_artist=slug_artist)

        return song_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_saved'] = self.object.saved_song_set.filter(user=self.request.user).exists()

        return context


class SongUpdateView(generic.UpdateView):
    model = Song
    form_class = SongForm
    template_name = 'player/song_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})

        return kwargs

    def get_object(self, queryset=None):
        slug_song = self.kwargs.get('slug_song')
        song_object = super().get_queryset().get(slug_song=slug_song, artist=self.request.user)

        return song_object

    def form_valid(self, form):
        messages.success(self.request, f'Song has been updated.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class SongDeleteView(generic.DeleteView):
    model = Song
    success_url = reverse_lazy('player:songs')

    def get_object(self, queryset=None):
        slug_song = self.kwargs.get('slug_song')
        song_object = super().get_queryset().get(slug_song=slug_song, artist=self.request.user)

        return song_object

    def form_valid(self, form):
        messages.success(self.request, f'Your song has been successfully deleted.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)


class SavedSongsListView(generic.ListView):
    model = SavedSong
    context_object_name = 'saved_songs'
    paginate_by = 10
    template_name = "player/saved_songs_list.html"

    def get_queryset(self):
        qs = super().get_queryset().select_related('song__artist').filter(user=self.request.user)
        search_val = self.request.GET.get('search_val', None)
        order_val = self.request.GET.get('order_by', '-pk')
        if search_val:
            qs = qs.filter(song__title__icontains=search_val).order_by(order_val)
        else:
            qs = qs.order_by(order_val)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qs_count'] = self.object_list.distinct().count()

        return context


def save_or_unsave_song(request, pk):
    song = get_object_or_404(Song, pk=pk)

    saved_song, created = SavedSong.objects.get_or_create(user=request.user, song=song)

    if created:
        messages.success(request, f'Song ({song.title}) saved')
    else:
        saved_song.delete()
        messages.success(request, f'Song ({song.title}) unsaved')

    return redirect(request.META.get('HTTP_REFERER'))


class AlbumsListView(generic.ListView):
    model = Album
    context_object_name = 'albums'
    paginate_by = 10
    template_name = "player/albums_list.html"

    def get_queryset(self):
        qs = super().get_queryset().select_related('artist')
        search_val = self.request.GET.get('search_val', None)
        order_val = self.request.GET.get('order_by', '-pk')
        if search_val:
            qs = qs.filter(title__icontains=search_val)
        qs = qs.order_by(order_val)

        return qs


class AlbumCreateView(generic.CreateView):
    form_class = AlbumForm
    template_name = 'player/object_create_base.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})

        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # show only songs that user has uploaded
        form.fields['songs'].queryset = Song.objects.filter(artist=self.request.user)
        return form

    def form_valid(self, form):
        # to specify user before saving form
        form.instance.artist = self.request.user
        messages.success(self.request, f'Album ({form.instance.title}) has been created.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'Album'

        return context

    def get_success_url(self):
        return self.object.get_absolute_url()


class AlbumDetailView(generic.DetailView):
    model = Album
    context_object_name = 'album'
    template_name = 'player/album.html'

    def get_object(self, queryset=None):
        slug_artist = self.kwargs.get('slug_artist')
        slug_album = self.kwargs.get('slug_album')
        album_object = super().get_queryset().select_related('artist').get(slug_album=slug_album, slug_artist=slug_artist)

        return album_object


class AlbumUpdateView(generic.UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'player/album_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})

        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # show only songs that user has uploaded
        form.fields['songs'].queryset = Song.objects.filter(artist=self.request.user)
        return form

    def get_object(self, queryset=None):
        slug_album = self.kwargs.get('slug_album')
        album_object = super().get_queryset().get(slug_album=slug_album, artist=self.request.user)

        return album_object

    def form_valid(self, form):
        messages.success(self.request, f'Album has been updated.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class AlbumDeleteView(generic.DeleteView):
    model = Album
    success_url = reverse_lazy('player:albums')

    def get_object(self, queryset=None):
        slug_album = self.kwargs.get('slug_album')
        album_object = super().get_queryset().get(slug_album=slug_album, artist=self.request.user)

        return album_object

    def form_valid(self, form):
        messages.success(self.request, f'Your album has been successfully deleted.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)


class PlaylistsListView(generic.ListView):
    model = Playlist
    context_object_name = 'playlists'
    paginate_by = 10
    template_name = "player/playlists_list.html"

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image_url'] = settings.MEDIA_URL + 'playlists/default.png'

        return context


class PlaylistCreateView(generic.CreateView):
    form_class = PlaylistForm
    template_name = 'player/object_create_base.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['songs'].queryset = SavedSong.objects.select_related('user', 'song').filter(user=self.request.user)
        return form

    def form_valid(self, form):
        # to specify user before saving form
        form.instance.user = self.request.user
        messages.success(self.request, f'Playlist ({form.instance.title}) has been created.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'Playlist'

        return context

    def get_success_url(self):
        return self.object.get_absolute_url()


class PlaylistDetailView(generic.DetailView):
    model = Playlist
    context_object_name = 'playlist'
    template_name = 'player/playlist.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        user = self.request.user
        playlist_object = super().get_queryset().select_related('user').prefetch_related('songs__song').get(
            pk=pk, user=user)

        return playlist_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image_url'] = settings.MEDIA_URL + 'playlists/default.png'

        return context


class PlaylistUpdateView(generic.UpdateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'player/playlist_update.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['songs'].queryset = SavedSong.objects.select_related('user', 'song').filter(user=self.request.user)
        return form

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        user = self.request.user
        playlist_object = super().get_queryset().get(pk=pk, user=user)

        return playlist_object

    def form_valid(self, form):
        messages.success(self.request, f'Playlist has been updated.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image_url'] = settings.MEDIA_URL + 'playlists/default.png'

        return context

    def get_success_url(self):
        return self.object.get_absolute_url()


class PlaylistDeleteView(generic.DeleteView):
    model = Playlist
    success_url = reverse_lazy('player:playlists')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        user = self.request.user
        playlist_object = super().get_queryset().get(pk=pk, user=user)

        return playlist_object

    def form_valid(self, form):
        messages.success(self.request, f'Your playlist has been successfully deleted.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)
