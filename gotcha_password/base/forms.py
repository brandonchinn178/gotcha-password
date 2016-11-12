from django import forms

from base.models import User

class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = forms.PasswordInput
        super(PasswordField, self).__init__(*args, **kwargs)

class CreateAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    password1 = PasswordField(label='Password')
    password2 = PasswordField(label='Verify password')
    consent = forms.BooleanField()

    @property
    def credential_fields(self):
        return [
            self[field]
            for field in ['username', 'email', 'password1', 'password2']
        ]

    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()

        if cleaned_data['password1'] != cleaned_data['password2']:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data

class AuthenticationForm(forms.Form):
    username = forms.CharField()
    password = PasswordField()

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('There is no user with that username.')
        return username
