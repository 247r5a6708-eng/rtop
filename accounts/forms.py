from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class PirateRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A pirate has already claimed this email, nakama.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class PirateLoginForm(forms.Form):
    username = forms.CharField(label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput)


class EmailChangeForm(forms.ModelForm):
    """Lets a logged-in pirate update the email address on their account."""
    current_password = forms.CharField(
        widget=forms.PasswordInput, label="Current password",
        help_text="Confirm it's really you before changing your email."
    )

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_order = ['email', 'current_password']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A pirate has already claimed this email, nakama.")
        return email

    def clean_current_password(self):
        password = self.cleaned_data.get('current_password')
        if not self.instance.check_password(password):
            raise ValidationError("That password doesn't match your account, nakama.")
        return password
