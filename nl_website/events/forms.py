from django import forms
from django.core.exceptions import ValidationError

from events.models import Event, Category


class AddEventForm(forms.ModelForm):

    cat = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Категория не выбрана", label="Категории")

    class Meta:
        model = Event
        fields = ['title', 'content', 'image', 'status', 'cat']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }
        labels = {'slug': 'URL'}

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise ValidationError("Длина превышает 50 символов")

        return title