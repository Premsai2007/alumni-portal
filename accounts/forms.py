from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=True)       # signal creates the Profile
        profile = user.profile
        profile.role = self.cleaned_data['role']
        profile.is_verified = (profile.role == 'student')  # alumni wait for approval
        profile.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['batch_year', 'department', 'company', 'designation',
                  'skills', 'location', 'bio', 'photo']
        widgets = {'bio': forms.Textarea(attrs={'rows': 4})}