# courses/forms.py
from django import forms
from .models import Enrollment

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['full_name', 'phone_number']
