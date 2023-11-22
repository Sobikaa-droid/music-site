from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes ':' as label suffix

        self.fields['username'].help_text = 'Letters, numbers and @/./+/-/_ only.'
        self.fields['password1'].help_text = '8-20 characters, letters and numbers, no spaces.'
        self.fields['password2'].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = CustomUser
        fields = ["username", "description", "image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes ':' as label suffix

