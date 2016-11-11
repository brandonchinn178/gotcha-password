from django import forms

from base.models import User

class CreateAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Verify password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()

        if cleaned_data['password1'] != cleaned_data['password2']:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data
