from django.urls import path

from . import views  # Use relative imports within the app

urlpatterns = [
    path("", views.index),
    path("forecast", views.plot_forecast),
    path("forecast/update", views.update_forecast),
    path("forecast-hl", views.plot_forecast_with_high_low),
    path("forecast-hl/update", views.update_forecast_with_high_low),
]
