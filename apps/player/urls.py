from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'player'

urlpatterns = [
    # song
    path('songs/', views.SongsListView.as_view(), name='songs'),
    path('upload/song/', login_required(views.SongCreateView.as_view(), login_url='users:register'),
         name='create_song'),
    path('song/<slug:slug_artist>/<slug:slug_song>/', views.SongDetailView.as_view(), name='song'),
    path('song-update/<slug:slug_artist>/<slug:slug_song>/update/', login_required(views.SongUpdateView.as_view(),
         login_url='users:register'), name='update_song'),
    path('song-delete/<int:pk>/', login_required(views.SongDeleteView.as_view(), login_url='users:register'),
         name='delete_song'),

    # saved song
    path('saved-songs/', login_required(views.SavedSongsListView.as_view(), login_url='users:register'),
         name='saved_songs'),
    path('save-song/<int:pk>/', login_required(views.save_or_unsave_song, login_url='users:register'),
         name='save_song'),

    # albums
    path('albums/', views.AlbumsListView.as_view(), name='albums'),
    path('upload/album/', login_required(views.AlbumCreateView.as_view(), login_url='users:register'),
         name='create_album'),
    path('album/<slug:slug_artist>/<slug:slug_album>/', views.AlbumDetailView.as_view(), name='album'),
    path('album-update/<slug:slug_artist>/<slug:slug_album>/', login_required(views.AlbumUpdateView.as_view(),
         login_url='users:register'), name='update_album'),
    path('album-delete/<int:pk>/', login_required(views.AlbumDeleteView.as_view(), login_url='users:register'),
         name='delete_album'),

    # playlist
    path('playlists/', login_required(views.PlaylistsListView.as_view(), login_url='users:register'), name='playlists'),
    path('upload/playlist/', login_required(views.PlaylistCreateView.as_view(), login_url='users:register'),
         name='create_playlist'),
    path('playlist/<int:pk>/<slug:slug>/', login_required(views.PlaylistDetailView.as_view(),
         login_url='users:register'), name='playlist'),
    path('playlist-update/<int:pk>/update/', login_required(views.PlaylistUpdateView.as_view(),
         login_url='users:register'), name='update_playlist'),
    path('playlist-delete/<int:pk>/', login_required(views.PlaylistDeleteView.as_view(), login_url='users:register'),
         name='delete_playlist'),
]
