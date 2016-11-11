from django.views.generic import TemplateView, FormView
from django.shortcuts import redirect

from base.forms import CreateAccountForm

class HomeView(TemplateView):
    """
    Shows a page that lets users decide if they want to create a new account
    or attempt to log in.
    """
    template_name = 'home.html'

class CreateAccountView(FormView):
    """
    Shows a page that lets a user choose a username and password.
    """
    template_name = 'create_account.html'
    form_class = CreateAccountForm

    def form_valid(self, form):
        """
        Save values in session and redirect to SetupImagesView
        """
        self.request.session['credentials'] = {
            'username': form.cleaned_data['username'],
            'password': form.cleaned_data['password1'],
        }
        return redirect('setup-images')

class SetupImagesView(TemplateView):
    """
    Shows a page with a random number of images (3-10)
    """
    template_name = 'setup_images.html'
