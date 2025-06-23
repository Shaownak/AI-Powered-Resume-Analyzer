import json
import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import JobApplicationForm, ResumeUploadForm
from .models import Job, JobApplication, Notification, Resume
from .notifications import notify_application_approved, notify_application_rejected
from .system_status import get_system_status

logger = logging.getLogger(__name__)

User = get_user_model()


# Create your views here.
def job_list(request):
    if request.method == "POST":
        # Handle job creation
        title = request.POST.get("title")
        description = request.POST.get("description")
        department = request.POST.get("department", "")
        location = request.POST.get("location", "")

        if title and description:
            # Get or create admin user
            user, created = User.objects.get_or_create(
                username="admin", defaults={"email": "admin@example.com", "is_superuser": True, "is_staff": True}
            )
            if created:
                user.set_password("adminpassword")
                user.save()

            Job.objects.create(title=title, description=description, posted_by=user)
            messages.success(request, f'Job "{title}" created successfully!')
            return redirect("job_list")
        else:
            messages.error(request, "Please fill in all required fields.")

    # Check if there are any jobs
    if Job.objects.count() == 0:
        # Create an admin user if it doesn't exist
        if not User.objects.filter(username="admin").exists():
            user = User.objects.create_superuser("admin", "admin@example.com", "adminpassword")
        else:
            user = User.objects.get(username="admin")
            # Create sample jobs
        Job.objects.create(
            title="Python Developer",
            description="We are looking for a Python developer with Django experience.",
            posted_by=user,
        )

        Job.objects.create(
            title="Frontend Developer",
            description="Looking for a Frontend developer with React and JavaScript skills.",
            posted_by=user,
        )

        Job.objects.create(
            title="Data Scientist",
            description="Data scientist position with experience in Python, pandas, and machine learning.",
            posted_by=user,
        )

    jobs = Job.objects.all().annotate(resume_count=Count("resumes"))
    total_resumes = Resume.objects.count()
    avg_score = Resume.objects.filter(score__isnull=False).aggregate(Avg("score"))["score__avg"]
    active_today = Resume.objects.filter(uploaded_at__date=timezone.now().date()).count()

    context = {
        "jobs": jobs,
        "total_resumes": total_resumes,
        "avg_score": avg_score,
        "active_today": active_today,
    }
    return render(request, "jobs/job_list.html", context)


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    resumes = Resume.objects.filter(job=job)  # ✅ Get resumes for the job

    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.job = job
            resume.save()
            return redirect("job_detail", job_id=job.id)
    else:
        form = ResumeUploadForm()

    return render(request, "jobs/job_detail.html", {"job": job, "form": form, "resumes": resumes})


def resume_upload(request, job_id):
    """Handle resume upload for a specific job"""
    job = get_object_or_404(Job, id=job_id, is_active=True)

    # Check if user is logged in and is an applicant
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to upload a resume.")
        return redirect("login")

    if request.user.user_type != "applicant":
        messages.error(request, "Only job applicants can upload resumes.")
        return redirect("job_detail", job_id=job.id)

    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resume = form.save(commit=False)
                resume.job = job
                resume.applicant = request.user
                resume.applicant_name = request.user.get_full_name() or request.user.username
                resume.save()
                messages.success(request, f"Resume uploaded successfully for {job.title}!")
                return redirect("job_detail", job_id=job.id)
            except Exception as e:
                messages.error(request, f"Error uploading resume: {str(e)}")
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = ResumeUploadForm()

    return render(request, "jobs/resume_upload.html", {"job": job, "form": form})


def resumes_list(request):
    """View for displaying all resumes with filtering and analytics"""
    resumes = Resume.objects.all().select_related("job").order_by("-uploaded_at")
    jobs = Job.objects.all()
    # Calculate stats
    high_score_count = resumes.filter(score__gte=80).count()
    avg_score = resumes.filter(score__isnull=False).aggregate(Avg("score"))["score__avg"]
    today_count = resumes.filter(uploaded_at__date=timezone.now().date()).count()

    context = {
        "resumes": resumes,
        "jobs": jobs,
        "high_score_count": high_score_count,
        "avg_score": avg_score,
        "today_count": today_count,
    }
    return render(request, "jobs/resumes_list.html", context)


def resume_detail(request, resume_id):
    """View for displaying individual resume details"""
    resume = get_object_or_404(Resume, id=resume_id)
    context = {
        "resume": resume,
    }
    return render(request, "jobs/resume_detail.html", context)


def analytics_dashboard(request):
    """Analytics dashboard view"""
    from django.db.models import Avg, Count

    # Get system status
    system_status = get_system_status()

    # Get statistics
    total_jobs = Job.objects.count()
    total_resumes = Resume.objects.count()
    avg_score = Resume.objects.filter(score__isnull=False).aggregate(Avg("score"))["score__avg"]
    # Score distribution
    high_score_count = Resume.objects.filter(score__gte=80).count()
    medium_score_count = Resume.objects.filter(score__gte=60, score__lt=80).count()
    low_score_count = Resume.objects.filter(score__lt=60).count()

    # Calculate percentages
    high_score_percentage = round((high_score_count / total_resumes * 100), 1) if total_resumes > 0 else 0
    medium_score_percentage = round((medium_score_count / total_resumes * 100), 1) if total_resumes > 0 else 0
    low_score_percentage = round((low_score_count / total_resumes * 100), 1) if total_resumes > 0 else 0

    # Top jobs by resume count
    top_jobs = Job.objects.annotate(resume_count=Count("resumes")).order_by("-resume_count")[:5]

    # Recent activity
    recent_resumes = Resume.objects.select_related("job").order_by("-uploaded_at")[:10]

    # Processing stats
    pending_resumes = Resume.objects.filter(scoring_status="pending").count()
    processing_resumes = Resume.objects.filter(scoring_status="processing").count()
    completed_resumes = Resume.objects.filter(scoring_status="completed").count()
    failed_resumes = Resume.objects.filter(scoring_status="failed").count()

    context = {
        "system_status": system_status,
        "total_jobs": total_jobs,
        "total_resumes": total_resumes,
        "avg_score": avg_score,
        "high_score_count": high_score_count,
        "medium_score_count": medium_score_count,
        "low_score_count": low_score_count,
        "high_score_percentage": high_score_percentage,
        "medium_score_percentage": medium_score_percentage,
        "low_score_percentage": low_score_percentage,
        "top_jobs": top_jobs,
        "recent_resumes": recent_resumes,
        "pending_resumes": pending_resumes,
        "processing_resumes": processing_resumes,
        "completed_resumes": completed_resumes,
        "failed_resumes": failed_resumes,
    }

    return render(request, "analytics.html", context)


# API Views for frontend
@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_job_list(request):
    if request.method == "GET":
        jobs = Job.objects.all()
        jobs_data = []
        for job in jobs:
            jobs_data.append(
                {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "posted_by": job.posted_by.username if job.posted_by else "Unknown",
                    "created_at": job.created_at.isoformat() if hasattr(job, "created_at") else None,
                    "resume_count": Resume.objects.filter(job=job).count(),
                }
            )
        return JsonResponse({"jobs": jobs_data})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            # Get or create admin user
            user, created = User.objects.get_or_create(
                username="admin", defaults={"email": "admin@example.com", "is_superuser": True}
            )
            if created:
                user.set_password("adminpassword")
                user.save()

            job = Job.objects.create(title=data["title"], description=data["description"], posted_by=user)
            return JsonResponse(
                {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "posted_by": job.posted_by.username,
                    "created_at": job.created_at.isoformat() if hasattr(job, "created_at") else None,
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def api_job_detail(request, job_id):
    try:
        job = get_object_or_404(Job, id=job_id)
        resumes = Resume.objects.filter(job=job)

        resumes_data = []
        for resume in resumes:
            resumes_data.append(
                {
                    "id": resume.id,
                    "name": resume.name,
                    "file": resume.file.url if resume.file else None,
                    "score": getattr(resume, "score", None),
                    "scoring_status": getattr(resume, "scoring_status", "pending"),
                    "uploaded_at": resume.uploaded_at.isoformat() if hasattr(resume, "uploaded_at") else None,
                }
            )

        return JsonResponse(
            {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "posted_by": job.posted_by.username if job.posted_by else "Unknown",
                "created_at": job.created_at.isoformat() if hasattr(job, "created_at") else None,
                "resumes": resumes_data,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def api_resume_list(request):
    try:
        resumes = Resume.objects.all()
        resumes_data = []
        for resume in resumes:
            resumes_data.append(
                {
                    "id": resume.id,
                    "name": resume.name,
                    "job_id": resume.job.id if resume.job else None,
                    "job_title": resume.job.title if resume.job else None,
                    "file": resume.file.url if resume.file else None,
                    "score": getattr(resume, "score", None),
                    "scoring_status": getattr(resume, "scoring_status", "pending"),
                    "uploaded_at": resume.uploaded_at.isoformat() if hasattr(resume, "uploaded_at") else None,
                }
            )
        return JsonResponse({"resumes": resumes_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def api_resume_detail(request, resume_id):
    try:
        resume = get_object_or_404(Resume, id=resume_id)
        return JsonResponse(
            {
                "id": resume.id,
                "name": resume.name,
                "job_id": resume.job.id if resume.job else None,
                "job_title": resume.job.title if resume.job else None,
                "file": resume.file.url if resume.file else None,
                "score": getattr(resume, "score", None),
                "scoring_status": getattr(resume, "scoring_status", "pending"),
                "uploaded_at": resume.uploaded_at.isoformat() if hasattr(resume, "uploaded_at") else None,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def api_upload_resume(request, job_id):
    if request.method == "POST":
        try:
            job = get_object_or_404(Job, id=job_id)

            if "file" in request.FILES:
                file = request.FILES["file"]
                name = request.POST.get("name", file.name)

                resume = Resume.objects.create(name=name, file=file, job=job)

                return JsonResponse(
                    {
                        "id": resume.id,
                        "name": resume.name,
                        "file": resume.file.url if resume.file else None,
                        "job_id": job.id,
                        "status": "uploaded",
                    }
                )
            else:
                return JsonResponse({"error": "No file provided"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@require_http_methods(["GET"])
def api_system_status(request):
    """API endpoint to get system status - simplified version"""
    try:
        # Simplified status check
        return JsonResponse(
            {
                "overall": {"status": "healthy", "message": "System is running", "timestamp": str(timezone.now())},
                "services": {"database": {"status": "online"}, "web_server": {"status": "online"}},
            }
        )
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return JsonResponse(
            {"error": str(e), "overall": {"status": "error", "message": "System status check failed"}}, status=500
        )


# Job Application Management Views


@login_required
def apply_for_job(request, job_id):
    """Apply for a specific job"""
    if request.user.user_type != "applicant":
        messages.error(request, "Only job applicants can apply for jobs.")
        return redirect("job_detail", job_id=job_id)

    job = get_object_or_404(Job, id=job_id, is_active=True)

    # Check if user already applied
    existing_application = JobApplication.objects.filter(job=job, applicant=request.user).first()
    if existing_application:
        messages.warning(request, "You have already applied for this job.")
        return redirect("job_detail", job_id=job_id)

    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Create resume record
                resume = Resume.objects.create(
                    job=job,
                    applicant=request.user,
                    applicant_name=request.user.get_full_name() or request.user.username,
                    resume_file=form.cleaned_data["resume_file"],
                    use_async=False,  # Use sync scoring for now
                )

                # Create job application
                application = JobApplication.objects.create(
                    job=job,
                    applicant=request.user,
                    resume=resume,
                    cover_letter=form.cleaned_data.get("cover_letter", ""),
                    status="pending",
                )

                messages.success(request, f'Your application for "{job.title}" has been submitted successfully!')
                return redirect("applicant_dashboard")

            except Exception as e:
                messages.error(request, f"Error submitting application: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobApplicationForm()

    return render(request, "jobs/apply_job.html", {"job": job, "form": form})


@login_required
def hr_applications(request):
    """View all applications for HR's jobs"""
    if request.user.user_type != "hr":
        messages.error(request, "Access denied. This area is for HR managers only.")
        return redirect("home")

    applications = (
        JobApplication.objects.filter(job__posted_by=request.user)
        .select_related("job", "applicant", "resume")
        .order_by("-applied_at")
    )

    return render(request, "jobs/hr_applications.html", {"applications": applications})


@login_required
def job_applications(request, job_id):
    """View all applications for a specific job"""
    job = get_object_or_404(Job, id=job_id)

    if request.user.user_type != "hr" or job.posted_by != request.user:
        messages.error(request, "Access denied.")
        return redirect("home")

    applications = JobApplication.objects.filter(job=job).select_related("applicant", "resume").order_by("-applied_at")

    # Calculate status counts
    pending_count = applications.filter(status="pending").count()
    approved_count = applications.filter(status="approved").count()
    rejected_count = applications.filter(status="rejected").count()

    return render(
        request,
        "jobs/job_applications.html",
        {
            "job": job,
            "applications": applications,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
        },
    )


@login_required
def approve_application(request, application_id):
    """Approve a job application"""
    if request.user.user_type != "hr":
        return JsonResponse({"success": False, "error": "Access denied. Only HR managers can approve applications."})

    try:
        application = get_object_or_404(JobApplication, id=application_id, job__posted_by=request.user)

        if request.method == "POST":
            # Check if application is still pending
            if application.status != "pending":
                return JsonResponse({"success": False, "error": f"Application is already {application.status}"})

            application.status = "approved"
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()

            # Send notification
            try:
                notify_application_approved(application)
                logger.info(f"✅ Application {application.id} approved by {request.user.username}")
            except Exception as e:
                logger.error(f"❌ Error sending approval notification: {e}")
                # Still return success since the approval itself worked

            return JsonResponse(
                {"success": True, "message": "Application approved successfully", "status": application.status}
            )
        else:
            return JsonResponse({"success": False, "error": "Invalid request method"})

    except Exception as e:
        logger.error(f"❌ Error approving application {application_id}: {e}")
        return JsonResponse({"success": False, "error": "An error occurred while approving the application"})


@login_required
def reject_application(request, application_id):
    """Reject a job application"""
    if request.user.user_type != "hr":
        return JsonResponse({"success": False, "error": "Access denied. Only HR managers can reject applications."})

    try:
        application = get_object_or_404(JobApplication, id=application_id, job__posted_by=request.user)

        if request.method == "POST":
            # Check if application is still pending
            if application.status != "pending":
                return JsonResponse({"success": False, "error": f"Application is already {application.status}"})

            application.status = "rejected"
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()

            # Send notification
            try:
                notify_application_rejected(application)
                logger.info(f"✅ Application {application.id} rejected by {request.user.username}")
            except Exception as e:
                logger.error(f"❌ Error sending rejection notification: {e}")
                # Still return success since the rejection itself worked

            return JsonResponse(
                {"success": True, "message": "Application rejected successfully", "status": application.status}
            )
        else:
            return JsonResponse({"success": False, "error": "Invalid request method"})

    except Exception as e:
        logger.error(f"❌ Error rejecting application {application_id}: {e}")
        return JsonResponse({"success": False, "error": "An error occurred while rejecting the application"})


@login_required
def hr_approved_applicants(request):
    """View all approved applicants by job"""
    if request.user.user_type != "hr":
        messages.error(request, "Access denied. This area is for HR managers only.")
        return redirect("home")

    # Group approved applications by job
    jobs_with_approved = (
        Job.objects.filter(posted_by=request.user, applications__status="approved")
        .prefetch_related("applications__applicant")
        .distinct()
    )

    job_data = []
    for job in jobs_with_approved:
        approved_applications = job.applications.filter(status="approved").select_related("applicant", "resume")
        job_data.append({"job": job, "approved_applications": approved_applications})

    return render(request, "jobs/approved_applicants.html", {"job_data": job_data})


@login_required
def create_job(request):
    """Create a new job posting (HR only)"""
    if request.user.user_type != "hr":
        messages.error(request, "Access denied. Only HR managers can post jobs.")
        return redirect("home")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        requirements = request.POST.get("requirements", "")
        location = request.POST.get("location", "")
        salary_range = request.POST.get("salary_range", "")
        employment_type = request.POST.get("employment_type", "full_time")

        if title and description:
            job = Job.objects.create(
                title=title,
                description=description,
                requirements=requirements,
                location=location,
                salary_range=salary_range,
                employment_type=employment_type,
                posted_by=request.user,
            )
            messages.success(request, f'Job "{title}" posted successfully!')
            return redirect("hr_dashboard")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, "jobs/create_job.html")
