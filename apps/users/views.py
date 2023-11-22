from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.views import generic
from django.shortcuts import get_object_or_404
from django.db.models import Count, Exists, OuterRef

from .forms import NewUserForm, UserUpdateForm
from .models import CustomUser
from apps.player.models import Song, Album, SavedSong


class UsersListView(generic.ListView):
    model = CustomUser
    context_object_name = 'users'
    paginate_by = 10
    template_name = "users/users_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(song_count=Count('song'))
        qs = qs.filter(song_count__gt=0)

        search_val = self.request.GET.get('search_val', None)
        order_val = self.request.GET.get('order_by', '-pk')
        if search_val:
            qs = qs.filter(username__icontains=search_val)
        qs = qs.order_by(order_val)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['qs_count'] = self.object_list.count()
        context['default_image_url'] = settings.MEDIA_URL + 'users/default.png'

        return context


class UserDetailView(generic.DetailView):
    model = CustomUser
    context_object_name = 'user'
    template_name = 'users/user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug_user = self.kwargs['slug']
        qs_songs = Song.objects.select_related('artist').filter(slug_artist=slug_user)
        qs_albums = Album.objects.select_related('artist').filter(slug_artist=slug_user)
        context['songs'] = qs_songs
        context['songs_count'] = qs_songs.count()
        context['albums'] = qs_albums
        context['albums_count'] = qs_albums.count()
        context['default_image_url'] = settings.MEDIA_URL + 'users/default.png'

        return context


class UserUpdateView(generic.UpdateView, LoginRequiredMixin):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'users/user_update.html'

    def get_object(self, queryset=None):
        user_object = get_object_or_404(CustomUser, pk=self.request.user.pk)

        return user_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image_url'] = settings.MEDIA_URL + 'users/default.png'

        return context

    def form_valid(self, form):
        messages.success(self.request, 'Profile has been updated.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class UserRegisterView(generic.FormView):
    form_class = NewUserForm
    success_url = reverse_lazy('home')
    template_name = 'users/register.html'

    def form_valid(self, form):
        form.save()
        new_user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
        )
        login(self.request, new_user)

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)


class UserLoginView(generic.FormView):
    form_class = AuthenticationForm
    success_url = reverse_lazy('home')
    template_name = 'users/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class UserDeleteView(generic.DeleteView):
    model = CustomUser
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, f'Your profile ({self.request.user.username}) has been successfully deleted.')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)

        return super().form_invalid(form)


class UserSongsListView(generic.ListView):
    model = Song
    context_object_name = 'songs'
    template_name = "users/user_songs_list.html"

    def get_queryset(self):
        qs = super().get_queryset().select_related('artist')
        user_slug = self.kwargs['slug']
        qs = qs.filter(artist__slug=user_slug)
        user = self.request.user

        # Annotate an additional field 'is_saved' to each song object
        if user.is_authenticated:
            qs = qs.annotate(is_saved=Exists(SavedSong.objects.filter(song=OuterRef('pk'), user=user)))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image_url'] = settings.MEDIA_URL + 'users/default.png'
        context['user'] = CustomUser.objects.get(slug=self.kwargs['slug'])

        return context


class UserAlbumsListView(generic.ListView):
    model = Album
    context_object_name = 'albums'
    template_name = "users/user_albums_list.html"

    def get_queryset(self):
        qs = super().get_queryset().select_related('artist')
        user_slug = self.kwargs['slug']
        qs = qs.filter(artist__slug=user_slug)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image_url'] = settings.MEDIA_URL + 'users/default.png'
        context['user'] = CustomUser.objects.get(slug=self.kwargs['slug'])

        return context
