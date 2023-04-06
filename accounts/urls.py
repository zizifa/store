from django.urls import path
from . import views


urlpatterns=[
    path("register/" , views.register , name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="dashboard"),
]