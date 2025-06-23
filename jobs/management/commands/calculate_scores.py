from django.core.management.base import BaseCommand

from jobs.ai import calculate_resume_score
from jobs.models import Resume


class Command(BaseCommand):
    help = "Recalculate scores for all resumes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recalculate scores even for resumes that already have scores",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if force:
            resumes = Resume.objects.all()
            self.stdout.write(f"Recalculating scores for all {len(resumes)} resumes...")
        else:
            resumes = Resume.objects.filter(score__isnull=True)
            self.stdout.write(f"Calculating scores for {len(resumes)} resumes with missing scores...")

        updated_count = 0
        error_count = 0

        for resume in resumes:
            if resume.resume_file:
                try:
                    score = calculate_resume_score(resume.resume_file.path, resume.job.description)
                    Resume.objects.filter(pk=resume.pk).update(score=score)
                    self.stdout.write(f"✅ {resume.applicant_name}: {score}%")
                    updated_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error calculating score for {resume.applicant_name}: {e}"))
                    # Set default score for failed calculations
                    Resume.objects.filter(pk=resume.pk).update(score=0.0)
                    error_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ No file for {resume.applicant_name}, setting score to 0"))
                Resume.objects.filter(pk=resume.pk).update(score=0.0)
                error_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Complete! Updated: {updated_count}, Errors: {error_count}"))
