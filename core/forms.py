from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.TextInput(attrs={'maxlength': 200, 'placeholder': "A rookie pirate setting sail."}),
            'avatar': forms.FileInput(attrs={'accept': 'image/png,image/jpeg,image/webp'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'content_type'):
            if avatar.size > 3 * 1024 * 1024:
                raise forms.ValidationError("Image is too large — please upload a file under 3MB.")
            allowed = ('image/jpeg', 'image/png', 'image/webp')
            if avatar.content_type not in allowed:
                raise forms.ValidationError("Only JPEG, PNG, or WEBP images are allowed.")
        return avatar
