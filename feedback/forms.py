from django import forms
from .models import SessionRequest, TechnicalReport
from django.core.exceptions import ValidationError
from datetime import date

class SessionRequestForm(forms.ModelForm):
    class Meta:
        model = SessionRequest
        fields = ['subject', 'delivery_mode', 'date', 'start_time', 'end_time']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Subject',
                'required': True
            }),
            'delivery_mode': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': True
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
                'placeholder': 'Start time',
                'required': True
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
                'placeholder': 'End time',
                'required': True
            }),
        }
    
    def clean_date(self):
        session_date = self.cleaned_data.get('date')
        if session_date and session_date < date.today():
            raise ValidationError('Date cannot be in the past')
        return session_date
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError('End time must be after start time')
        
        return cleaned_data

class TechnicalReportForm(forms.ModelForm):
    class Meta:
        model = TechnicalReport
        fields = ['problem_description']
        widgets = {
            'problem_description': forms.Textarea(attrs={
                'class': 'report-textarea',
                'id': 'problemText',
                'maxlength': '150',
                'placeholder': 'Describe your technical issue',
                'rows': 6,
            }),
        }
        labels = {
            'problem_description': '',  # Không hiển thị label
        }
    
    def clean_problem_description(self):
        description = self.cleaned_data.get('problem_description')
        if not description or not description.strip():
            raise forms.ValidationError('Please describe your technical problem!')
        if len(description) > 150:
            raise forms.ValidationError('Description must not exceed 150 characters!')
        return description.strip()