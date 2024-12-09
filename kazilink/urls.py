from django.urls import path
from . import views



urlpatterns = [
        path('', views.home_page, name="kazilink_home"),
        path('contact/', views.contact_page, name="kazilink_contact"),
        path('about/', views.about_page, name="kazilink_about"),
        path('services/', views.services_page, name="kazilink_services"),
]