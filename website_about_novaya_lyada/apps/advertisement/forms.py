from django import forms
from django.utils import timezone
from django.forms import ModelForm
from website_about_novaya_lyada.apps.advertisement.models import Advertisement, AdvertisementCategory


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class AddAdvertisementForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=AdvertisementCategory.objects.all(),
        required=False,
        label='Категория',
        empty_label='Категория не выбрана',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    dedline_publish = forms.DateTimeField(
        required=True,
        label='Дата окончания публикации',
        widget=DateTimeLocalInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Advertisement
        fields = ['title', 'content', 'price', 'image', 'category', 'phone', 'address', 'dedline_publish']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_dedline_publish(self):
        value = self.cleaned_data['dedline_publish']
        # if USE_TZ True, compare with now(); value assumed naive-local from widget; tolerate future only
        if value <= timezone.now():
            raise forms.ValidationError('Дата окончания публикации должна быть в будущем')
        return value


class UpdateAdvertisementForm(AddAdvertisementForm):
    class Meta(AddAdvertisementForm.Meta):
        fields = ['title', 'content', 'price', 'image', 'category', 'phone', 'address', 'dedline_publish', 'status']

