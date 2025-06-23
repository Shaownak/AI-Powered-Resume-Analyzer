from django.urls import path

from . import views

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("job/<int:job_id>/", views.job_detail, name="job_detail"),
    # Job application management
    path("job/<int:job_id>/apply/", views.apply_for_job, name="apply_for_job"),
    path("applications/", views.hr_applications, name="hr_applications"),
    path("job/<int:job_id>/applications/", views.job_applications, name="job_applications"),
    path("applications/<int:application_id>/approve/", views.approve_application, name="approve_application"),
    path("applications/<int:application_id>/reject/", views.reject_application, name="reject_application"),
    path("approved-applicants/", views.hr_approved_applicants, name="hr_approved_applicants"),
    path("create-job/", views.create_job, name="create_job"),
    # Resume management URLs
    path("resumes/", views.resumes_list, name="resumes_list"),
    path("resumes/<int:resume_id>/", views.resume_detail, name="resume_detail"),
    path("upload-resume/", views.api_upload_resume, name="upload_resume"),
    path("job/<int:job_id>/upload-resume/", views.resume_upload, name="job_upload_resume"),
    # Analytics and other pages
    path("analytics/", views.analytics_dashboard, name="analytics"),
    # API endpoints for frontend
    path("api/jobs/", views.api_job_list, name="api_job_list"),
    path("api/jobs/<int:job_id>/", views.api_job_detail, name="api_job_detail"),
    path("api/resumes/", views.api_resume_list, name="api_resume_list"),
    path("api/resumes/<int:resume_id>/", views.api_resume_detail, name="api_resume_detail"),
    path("api/jobs/<int:job_id>/upload-resume/", views.api_upload_resume, name="api_upload_resume"),
]
