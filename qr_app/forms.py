import os
from django import forms
from qr_app.models import MediaFile


class MediaFileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = MediaFile
        fields = ['file', 'password']


class DeleteMediaFileForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)