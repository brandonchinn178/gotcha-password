from django.views.generic import TemplateView

class HomeView(TemplateView):
    """
    Shows a page that lets users decide if they want to create a new account
    or attempt to log in.
    """
    template_name = 'home.html'
