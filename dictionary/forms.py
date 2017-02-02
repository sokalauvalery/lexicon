from django import forms
from .models import TextFile
from django.forms import ModelForm


class UploadFileForm(ModelForm):
    class Meta:
        model = TextFile
        fields = ['title', 'file']
