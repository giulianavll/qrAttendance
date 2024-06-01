from . import views

from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login_view"),
    path("reports", views.report, name="report"),
    path("logout", views.logout_view, name="logout_view"),
    path("api/attendance", views.attendance, name="attendance"),
]
