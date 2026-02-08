# courses/forms.py
# this is an enrollment form for students to enroll in courses
from django import forms
from .models import Enrollment
from .models import Lesson

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'order']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['full_name', 'phone_number']
