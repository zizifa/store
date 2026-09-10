from django.urls import path
from . import views


urlpatterns = [
    # Passwordless customer login (two-step phone -> OTP), no password fields.
    path("login/", views.customer_login, name="login"),

    # Legacy customer password/email flows are disabled for customers.
    # Students: keep name-based links working but redirect to passwordless login.
    path("register/", views.register_disabled, name="register"),
    path("forgotpassword/", views.forgotpassword_disabled, name="forgotpassword"),
    path(
        "resetpassword_validate/<uidb64>/<token>",
        views.resetpassword_disabled,
        name="resetpassword_validate",
    ),

    path("logout/", views.logout, name="logout"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="dashboard_empty"),

    path('my-orders/', views.my_orders, name="my_orders"),
    path('edit-profile/', views.edit_profile, name="edit_profile"),
    path('change-password/', views.change_password, name="change_password"),
    path('order-detail/<int:order_id>/', views.order_detail, name="order_detail"),

    # OTP authentication page routes (server-rendered, kept for compatibility)
    path('otp-login/', views.otp_login_request, name='otp_login'),
    path('otp-verify/', views.otp_login_verify, name='otp_verify'),
    path('otp-logout/', views.otp_logout, name='otp_logout'),
    path('otp-dashboard/', views.otp_dashboard, name='otp_dashboard'),

]
