from django import forms
from .models import Tutor

class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'accept': 'image/*',
                'id': 'avatar-input'
            })
        }

class ExpertiseUpdateForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['expertise']
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