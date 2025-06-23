from django.db import models
from django.contrib.auth import get_user_model
import requests
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True, help_text="Job requirements and qualifications")
    location = models.CharField(max_length=100, blank=True)
    salary_range = models.CharField(max_length=50, blank=True)
    employment_type = models.CharField(max_length=20, choices=[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ], default='full_time')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'hr'})
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    application_deadline = models.DateTimeField(null=True, blank=True)    
    def __str__(self):
        return self.title


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'applicant'})
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='reviewed_applications')
    cover_letter = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="HR notes")
    
    class Meta:
        unique_together = ('job', 'applicant')
    
    def __str__(self):
        return f"{self.applicant.get_full_name()} - {self.job.title}"


class Resume(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Score'),
        ('processing', 'Processing'),
        ('completed', 'Scored'),
        ('failed', 'Failed'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='resumes')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'applicant'}, null=True, blank=True)
    applicant_name = models.CharField(max_length=255)
    resume_file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    scoring_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    task_id = models.CharField(max_length=255, null=True, blank=True)
    use_async = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.resume_file and self.score is None:
            if self.use_async:
                self._score_resume_async()
            else:
                self._score_resume_sync()
    
    def _score_resume_async(self):
        """Score resume using async Celery task"""
        try:
            self.scoring_status = 'processing'
            Resume.objects.filter(pk=self.pk).update(scoring_status='processing')
            
            with open(self.resume_file.path, 'rb') as f:
                response = requests.post(
                    'http://127.0.0.1:8001/score/',
                    files={'file': f},
                    data={
                        'job_description': self.job.description,
                        'async_mode': 'true'
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'task_id' in result:
                        self.task_id = result['task_id']
                        Resume.objects.filter(pk=self.pk).update(
                            task_id=self.task_id,
                            scoring_status='processing'
                        )
                        logger.info(f"✅ Async scoring queued for {self.applicant_name}, task: {self.task_id}")
                    else:
                        # Got immediate result
                        self.score = result.get("score", 0.0)
                        self.scoring_status = 'completed'
                        Resume.objects.filter(pk=self.pk).update(
                            score=self.score,
                            scoring_status='completed'
                        )
                        logger.info(f"✅ Immediate score for {self.applicant_name}: {self.score}%")
                else:
                    raise Exception(f"Microservice error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"❌ Async scoring failed for {self.applicant_name}: {e}")
            self._fallback_scoring()
    
    def _score_resume_sync(self):
        """Score resume synchronously (original method)"""
        try:
            self.scoring_status = 'processing'
            Resume.objects.filter(pk=self.pk).update(scoring_status='processing')
            
            with open(self.resume_file.path, 'rb') as f:
                response = requests.post(
                    'http://127.0.0.1:8001/score/',
                    files={'file': f},
                    data={'job_description': self.job.description}
                )
                if response.status_code == 200:
                    self.score = response.json().get("score", 0.0)
                    self.scoring_status = 'completed'
                    Resume.objects.filter(pk=self.pk).update(
                        score=self.score,
                        scoring_status='completed'
                    )
                    logger.info(f"✅ Scored resume for {self.applicant_name}: {self.score}%")
                else:
                    raise Exception(f"Microservice error: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Microservice scoring failed for {self.applicant_name}: {e}")
            self._fallback_scoring()
    
    def _fallback_scoring(self):
        """Fallback to local scoring if microservice fails"""
        try:
            from .ai import calculate_resume_score
            self.score = calculate_resume_score(self.resume_file.path, self.job.description)
            self.scoring_status = 'completed'
            Resume.objects.filter(pk=self.pk).update(
                score=self.score,
                scoring_status='completed'
            )
            logger.info(f"✅ Fallback scoring for {self.applicant_name}: {self.score}%")
        except Exception as fallback_error:
            logger.error(f"❌ Fallback scoring failed for {self.applicant_name}: {fallback_error}")
            Resume.objects.filter(pk=self.pk).update(
                score=0.0,
                scoring_status='failed'
            )
    
    def check_async_score(self):
        """Check async task status and update score if ready"""
        if not self.task_id or self.scoring_status != 'processing':
            return False
            
        try:
            response = requests.get(f'http://127.0.0.1:8001/task/{self.task_id}')
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                
                if status == 'completed' and 'score' in result:
                    self.score = result['score']
                    self.scoring_status = 'completed'
                    Resume.objects.filter(pk=self.pk).update(
                        score=self.score,
                        scoring_status='completed'
                    )                    logger.info(f"✅ Async score completed for {self.applicant_name}: {self.score}%")
                    return True
                elif status == 'failed':
                    self.scoring_status = 'failed'
                    Resume.objects.filter(pk=self.pk).update(scoring_status='failed')
                    logger.error(f"❌ Async scoring failed for {self.applicant_name}")
                    self._fallback_scoring()
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Error checking async task {self.task_id}: {e}")
        
        return False

    def __str__(self):
        return self.applicant_name


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
        ('new_job_match', 'New Job Match'),
        ('resume_scored', 'Resume Scored'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"