from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse
from jobs.models import Job, JobApplication, Resume
from jobs.notifications import get_user_notifications
from .forms import ApplicantSignUpForm, HRSignUpForm, LoginForm
from .models import CustomUser

def home(request):
    """Landing page that introduces the system"""
    return render(request, 'accounts/home.html')

def login_view(request):
    """Universal login for both applicants and HR"""
    if request.user.is_authenticated:
        return redirect_after_login(request.user)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect_after_login(user)
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def applicant_signup(request):
    """Sign up for job applicants"""
    if request.method == 'POST':
        form = ApplicantSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your applicant account has been created successfully.')
            return redirect('applicant_dashboard')
    else:
        form = ApplicantSignUpForm()
    
    return render(request, 'accounts/applicant_signup.html', {'form': form})

def hr_signup(request):
    """Sign up for HR managers"""
    if request.method == 'POST':
        form = HRSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your HR account has been created successfully.')
            return redirect('hr_dashboard')
    else:
        form = HRSignUpForm()
    
    return render(request, 'accounts/hr_signup.html', {'form': form})

def logout_view(request):
    """Logout and redirect to home"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def redirect_after_login(user):
    """Redirect user to appropriate dashboard based on user type"""
    if user.user_type == 'hr':
        return redirect('hr_dashboard')
    elif user.user_type == 'applicant':
        return redirect('applicant_dashboard')
    else:
        return redirect('admin:index')  # For admin users

@login_required
def profile_view(request):
    """User profile page with update functionality"""
    if request.method == 'POST':
        # Update user information
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        
        if user.user_type == 'applicant':
            # Update or create applicant profile
            from .models import ApplicantProfile
            profile, created = ApplicantProfile.objects.get_or_create(user=user)
            profile.full_name = request.POST.get('full_name', '')
            profile.location = request.POST.get('location', '')
            profile.bio = request.POST.get('bio', '')
            profile.save()
            
        elif user.user_type == 'hr':
            # Update or create HR profile
            from .models import HRProfile
            profile, created = HRProfile.objects.get_or_create(user=user)
            profile.company_name = request.POST.get('company_name', '')
            profile.job_title = request.POST.get('job_title', '')
            profile.company_description = request.POST.get('company_description', '')
            profile.save()
            
            # Update phone in the main user model
            user.phone = request.POST.get('phone', '')
            user.save()
        
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')
    
    if request.user.user_type == 'applicant':
        return render(request, 'accounts/applicant_profile.html')
    elif request.user.user_type == 'hr':
        return render(request, 'accounts/hr_profile.html')
    else:
        return redirect('admin:index')

@login_required
def applicant_dashboard(request):
    """Dashboard for job applicants"""
    if request.user.user_type != 'applicant':
        messages.error(request, 'Access denied. This area is for job applicants only.')
        return redirect('home')
    
    # Get user's applications
    applications = JobApplication.objects.filter(applicant=request.user).select_related('job', 'resume').order_by('-applied_at')
    
    # Get available jobs (active jobs that user hasn't applied to)
    applied_job_ids = applications.values_list('job_id', flat=True)
    available_jobs = Job.objects.filter(is_active=True).exclude(id__in=applied_job_ids).order_by('-posted_at')[:5]
    
    # Get recent notifications
    notifications = get_user_notifications(request.user).filter(is_read=False)[:5]
    
    context = {
        'applications': applications,
        'available_jobs': available_jobs,
        'notifications': notifications,
        'total_applications': applications.count(),
        'pending_applications': applications.filter(status='pending').count(),
        'approved_applications': applications.filter(status='approved').count(),
    }
    
    return render(request, 'accounts/applicant_dashboard.html', context)

@login_required  
def hr_dashboard(request):
    """Dashboard for HR managers"""
    if request.user.user_type != 'hr':
        messages.error(request, 'Access denied. This area is for HR managers only.')
        return redirect('home')
    
    # Get HR's posted jobs
    posted_jobs = Job.objects.filter(posted_by=request.user).order_by('-posted_at')
    
    # Get applications for HR's jobs
    applications = JobApplication.objects.filter(job__posted_by=request.user).select_related('job', 'applicant', 'resume').order_by('-applied_at')
    
    # Statistics
    total_applications = applications.count()
    pending_applications = applications.filter(status='pending').count()
    approved_applications = applications.filter(status='approved').count()
    rejected_applications = applications.filter(status='rejected').count()
    
    context = {
        'posted_jobs': posted_jobs,
        'applications': applications[:10],  # Latest 10 applications
        'total_jobs': posted_jobs.count(),
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'rejected_applications': rejected_applications,
    }
    
    return render(request, 'accounts/hr_dashboard.html', context)

@login_required
def applicant_notifications(request):
    """View all notifications for applicant"""
    if request.user.user_type != 'applicant':
        messages.error(request, 'Access denied. This area is for job applicants only.')
        return redirect('home')
    
    # Get all notifications for the user
    notifications = get_user_notifications(request.user).order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 10)  # Show 10 notifications per page
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    # Get unread count
    unread_count = get_user_notifications(request.user).filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'accounts/applicant_notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    if request.method == 'POST':
        try:
            from jobs.models import Notification
            notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})
