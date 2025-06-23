from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import CustomUser, ApplicantProfile, HRProfile

class ApplicantSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'phone', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-3 border border-secondary-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200'
        
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['email'].widget.attrs['placeholder'] = 'your.email@example.com'
        self.fields['full_name'].widget.attrs['placeholder'] = 'Your Full Name'
        self.fields['phone'].widget.attrs['placeholder'] = '+1 (555) 123-4567'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a strong password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = 'applicant'
        if commit:
            user.save()
            # Create applicant profile
            ApplicantProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name']
            )
        return user

class HRSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    company_name = forms.CharField(max_length=100, required=True)
    job_title = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'company_name', 'job_title', 'phone', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-3 border border-secondary-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200'
            
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['email'].widget.attrs['placeholder'] = 'hr@company.com'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['company_name'].widget.attrs['placeholder'] = 'Your Company Name'
        self.fields['job_title'].widget.attrs['placeholder'] = 'HR Manager'
        self.fields['phone'].widget.attrs['placeholder'] = '+1 (555) 123-4567'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a strong password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = 'hr'
        if commit:
            user.save()
            # Create HR profile
            HRProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                job_title=self.cleaned_data.get('job_title', '')
            )
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-3 border border-secondary-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200'
            
        self.fields['username'].widget.attrs['placeholder'] = 'Username or Email'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to authenticate with username first, then email
            user = authenticate(username=username, password=password)
            if not user:
                # Try with email
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if not user:
                raise forms.ValidationError("Invalid username/email or password.")
            
            self.user = user
        return self.cleaned_data
