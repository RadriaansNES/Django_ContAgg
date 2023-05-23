from django.views.generic import ListView
from .models import Episode

## create homepageview with class based view
class HomePageView(ListView):
    template_name = "homepage.html"
    model = Episode

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # override content
        context["episodes"] = Episode.objects.filter().order_by("-pub_date")[:10] # filter to recent 10
        return context