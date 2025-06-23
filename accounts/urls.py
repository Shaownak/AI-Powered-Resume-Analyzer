from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/applicant/", views.applicant_signup, name="applicant_signup"),
    path("signup/hr/", views.hr_signup, name="hr_signup"),
    path("profile/", views.profile_view, name="profile"),
    path("dashboard/applicant/", views.applicant_dashboard, name="applicant_dashboard"),
    path("dashboard/hr/", views.hr_dashboard, name="hr_dashboard"),
    path("notifications/", views.applicant_notifications, name="applicant_notifications"),
    path("notifications/<int:notification_id>/mark-read/", views.mark_notification_read, name="mark_notification_read"),
]
