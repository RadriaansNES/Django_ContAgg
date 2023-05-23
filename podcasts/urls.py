from django.urls import path
from .views import HomePageView

## add path for homepageview class
urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
]