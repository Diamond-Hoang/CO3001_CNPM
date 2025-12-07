from django import forms
from .models import Student

class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'accept': 'image/*',
                'id': 'avatar-input'
            })
        }

class SupportNeedsUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['sp_needs']
        widgets = {
            'sp_needs': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Nhập môn học hoặc lĩnh vực cần hỗ trợ...',
                'class': 'form-control'
            })
        }
        labels = {
            'sp_needs': 'Môn học cần giúp đỡ'
        }