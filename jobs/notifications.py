from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Notification
import logging

logger = logging.getLogger(__name__)


def create_notification(recipient, notification_type, title, message, job=None, application=None, sender=None):
    """Create a notification for a user"""
    try:
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            job=job,
            application=application
        )
        
        # Send email notification
        send_notification_email(notification)
        
        return notification
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        return None


def send_notification_email(notification):
    """Send email notification to recipient"""
    try:
        if notification.is_email_sent:
            return
            
        # Email templates based on notification type
        email_templates = {
            'application_approved': {
                'subject': f'🎉 Your application for {notification.job.title} has been approved!',
                'template': 'emails/application_approved.html'
            },
            'application_rejected': {
                'subject': f'Application Update - {notification.job.title}',
                'template': 'emails/application_rejected.html'
            },
            'resume_scored': {
                'subject': f'Resume Analysis Complete - {notification.job.title}',
                'template': 'emails/resume_scored.html'
            },
            'new_job_match': {
                'subject': f'New Job Match: {notification.job.title}',
                'template': 'emails/new_job_match.html'
            },
        }
        
        email_config = email_templates.get(notification.notification_type)
        if not email_config:
            logger.warning(f"No email template for notification type: {notification.notification_type}")
            return
            
        # Render HTML email content
        html_message = render_to_string(email_config['template'], {
            'notification': notification,
            'recipient': notification.recipient,
            'job': notification.job,
            'application': notification.application,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=email_config['subject'],
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Mark as sent
        notification.is_email_sent = True
        notification.save()
        
        logger.info(f"✅ Email sent to {notification.recipient.email} for {notification.notification_type}")
        
    except Exception as e:
        logger.error(f"❌ Error sending email to {notification.recipient.email}: {e}")


def notify_application_approved(application):
    """Send notification when application is approved"""
    title = f"Application Approved - {application.job.title}"
    message = f"Congratulations! Your application for {application.job.title} has been approved. You will be contacted soon with next steps."
    
    return create_notification(
        recipient=application.applicant,
        notification_type='application_approved',
        title=title,
        message=message,
        job=application.job,
        application=application,
        sender=application.reviewed_by
    )


def notify_application_rejected(application):
    """Send notification when application is rejected"""
    title = f"Application Update - {application.job.title}"
    message = f"Thank you for your interest in {application.job.title}. After careful consideration, we have decided to move forward with other candidates."
    
    return create_notification(
        recipient=application.applicant,
        notification_type='application_rejected',
        title=title,
        message=message,
        job=application.job,
        application=application,
        sender=application.reviewed_by
    )


def notify_resume_scored(resume):
    """Send notification when resume is scored"""
    title = f"Resume Analysis Complete - {resume.job.title}"
    message = f"Your resume for {resume.job.title} has been analyzed. Score: {resume.score:.2f}%"
    
    if resume.applicant:
        return create_notification(
            recipient=resume.applicant,
            notification_type='resume_scored',
            title=title,
            message=message,
            job=resume.job
        )


def get_user_notifications(user, unread_only=False):
    """Get notifications for a user"""
    notifications = user.notifications.all()
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    return notifications


def mark_notification_read(notification_id, user):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, recipient=user)
        notification.is_read = True
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False
