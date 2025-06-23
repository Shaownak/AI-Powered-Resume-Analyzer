import os

try:
    content = """from django.db import models
from django.contrib.auth.models import User
import requests


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class Resume(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="resumes")
    applicant_name = models.CharField(max_length=255)
    resume_file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.resume_file and self.score is None:
            try:
                with open(self.resume_file.path, "rb") as f:
                    response = requests.post(
                        "http://127.0.0.1:8001/score/",
                        files={"file": f},
                        data={"job_description": self.job.description}
                    )
                    if response.status_code == 200:
                        self.score = response.json().get("score")
                        Resume.objects.filter(pk=self.pk).update(score=self.score)
                        print(f"Scored resume for {self.applicant_name}: {self.score}%")
                    else:
                        raise Exception(f"Microservice error: {response.status_code}")
            except Exception as e:
                try:
                    from .ai import calculate_resume_score
                    self.score = calculate_resume_score(self.resume_file.path, self.job.description)
                    Resume.objects.filter(pk=self.pk).update(score=self.score)
                    print(f"Fallback scoring for {self.applicant_name}: {self.score}%")
                except Exception as fallback_error:
                    Resume.objects.filter(pk=self.pk).update(score=0.0)

    def __str__(self):
        return self.applicant_name
"""

    with open("jobs/models.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("models.py created successfully")
    print(f'File size: {os.path.getsize("jobs/models.py")} bytes')
except Exception as e:
    print(f"Error: {e}")
