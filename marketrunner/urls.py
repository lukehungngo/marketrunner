from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

# Home view that renders the index.html template


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),  # Include app-level URLs
]
