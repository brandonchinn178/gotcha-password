from django.views.generic import TemplateView, FormView
from django.shortcuts import redirect

from random import randint

from base.forms import *
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
        Save values in session and redirect to CreateImagesView
        """
        self.request.session['credentials'] = {
            'username': form.cleaned_data['username'],
            'email': form.cleaned_data['email'],
            'raw_password': form.cleaned_data['password1'],
            'seed': get_random_seed(),
            'num_images': randint(3, 7),
        }
        return redirect('create-images')

class CreateImagesView(TemplateView):
    """
    Shows a page with the images for the user to label
    """
    template_name = 'create_images.html'

    def get_context_data(self, **kwargs):
        context = super(CreateImagesView, self).get_context_data(**kwargs)

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
        labels = extract_labels(request.POST)

        User.objects.create(labels=labels, **credentials)

        return redirect('create-success')

class CreateSuccessView(TemplateView):
    """
    Shows a page informing the user that their account was successfully created.
    """
    template_name = 'create_success.html'

class LoginView(FormView):
    """
    Shows a page that lets the user log in with a given username and password.
    """
    template_name = 'login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        self.request.session['credentials'] = form.cleaned_data
        return redirect('login-verify')

class LoginVerifyView(TemplateView):
    """
    Shows a page that displays the images and labels to the user
    """
    template_name = 'login_verify.html'

    def get_context_data(self, **kwargs):
        context = super(LoginVerifyView, self).get_context_data(**kwargs)

        credentials = self.request.session['credentials']
        user = User.objects.get(username=credentials['username'])
        image_seed = extract(credentials['password'], user.seed)
        context['images'] = generate_images(user.num_images, image_seed)
        context['labels'] = Label.objects.filter(user=user)

        context['svg_width'] = SVG_WIDTH
        context['svg_height'] = SVG_HEIGHT

        return context

    def post(self, request, *args, **kwargs):
        """
        Accepts the list of labels with the names "label-<image_num>". Each name is mapped
        to the value of the label, which should match the user's permutation
        """
        credentials = self.request.session['credentials']
        user = User.objects.get(username=credentials['username'])
        labels = map(int, extract_labels(request.POST))

        # typically, here is where authentication would happen. instead of authenticating,
        # show a page with user results and save in a LoginAttempt
        right_password = user.check_password(credentials['password'], labels)
        permutation = user.get_permutation()
        correct_images = sum([
            1 if val == permutation[i] else 0
            for i, val in enumerate(labels)
        ])

        login = LoginAttempt.objects.create(
            user=user,
            right_password=right_password,
            correct_images=correct_images,
            password=hash_once(credentials['password'], user.salt),
            permutation=','.join(map(str, labels)),
        )
        print 'Running benchmarks for %s...' % login
        background_process(run_benchmarks, login, False)

        self.request.session['right_password'] = right_password
        self.request.session['correct_images'] = correct_images

        return redirect('login-success')

class LoginSuccessView(TemplateView):
    """
    Shows a success page that shows the user how many labels they correctly matched
    """
    template_name = 'login_success.html'

    def get_context_data(self, **kwargs):
        context = super(LoginSuccessView, self).get_context_data(**kwargs)

        credentials = self.request.session['credentials']
        user = User.objects.get(username=credentials['username'])
        correct_images = self.request.session['correct_images']

        context['user'] = user
        context['right_password'] = self.request.session['right_password']
        context['correct_images'] = correct_images
        context['num_images'] = user.num_images
        context['percentage'] = '%0.1f' % (float(correct_images) / user.num_images * 100)

        return context
