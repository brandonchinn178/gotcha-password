from django.views.generic import TemplateView, FormView
from django.shortcuts import redirect

from random import randint

from base.forms import CreateAccountForm
from base.models import *
from base.utils import *

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
            'raw_password': form.cleaned_data['password1'],
            'seed': get_random_seed(),
            'num_images': randint(3, 7),
        }
        return redirect('setup-images')

class SetupImagesView(TemplateView):
    """
    Shows a page with the images for the user to label
    """
    template_name = 'setup_images.html'

    def get_context_data(self, **kwargs):
        context = super(SetupImagesView, self).get_context_data(**kwargs)

        credentials = self.request.session['credentials']
        image_seed = extract(credentials['raw_password'], credentials['seed'])
        context['images'] = generate_images(credentials['num_images'], image_seed)

        context['svg_width'] = SVG_WIDTH
        context['svg_height'] = SVG_HEIGHT

        return context

    def post(self, request, *args, **kwargs):
        """
        Accepts the list of labels with the names "label-<num>". The labels have already
        been validated on the client side.
        """
        credentials = self.request.session['credentials']
        labels = [
            (int(name[6:]), text)
            for name, text in request.POST.items()
            if name.startswith('label-')
        ]

        User.objects.create(labels=labels, **credentials)

        return redirect('create-success')

class CreateSuccessView(TemplateView):
    """
    Shows a page informing the user that their account was successfully created.
    """
    template_name = 'create_success.html'
