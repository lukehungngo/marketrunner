from django.urls import path

from . import views  # Use relative imports within the app

urlpatterns = [
    path("forecast", views.plot_forecast),
    path("forecast/update", views.update_forecast),
]
