from django import forms
from .models import Resume, Job


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['resume_file']
        widgets = {
            'resume_file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200',
                'accept': '.pdf,.doc,.docx'
            })
        }

class JobApplicationForm(forms.Form):
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200',
            'rows': 5,
            'placeholder': 'Tell us why you are interested in this position...'
        }),
        required=False,
        label='Cover Letter'
    )
    resume_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200',
            'accept': '.pdf,.doc,.docx'
        }),
        label='Upload Resume'
    )