from django.urls import path
from . import views


urlpatterns=[
    path("register/" , views.register , name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="dashboard"),

    path("forgotpassword/", views.forgotpassword , name="forgotpassword"),
    path('resetpassword_validate/<uidb64>/<token>', views.resetpassword_validate , name="resetpassword_validate"),

    path('my-orders/',views.my_orders , name="my_orders"),
    path('edit-profile/',views.edit_profile , name="edit_profile"),
]
