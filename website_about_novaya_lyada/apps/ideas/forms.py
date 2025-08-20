from django import forms
from .models import ImprovementIdea, IdeaComment


class IdeaForm(forms.ModelForm):
    class Meta:
        model = ImprovementIdea
        fields = ['title', 'description', 'proposed_solution', 'location', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткое название вашей идеи'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите проблему или идею подробнее...'
            }),
            'proposed_solution': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Как вы предлагаете решить эту проблему?'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Где именно в Новой Ляде?'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = IdeaComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ваш комментарий...'
            })
        }
