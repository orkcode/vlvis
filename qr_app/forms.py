import os
from django import forms
from qr_app.models import MediaFile
import tempfile
from moviepy.editor import VideoFileClip


class MediaFileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = MediaFile
        fields = ['file', 'password']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        max_duration = 150  # Максимальная длительность видео в секундах

        if file and file.content_type in ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-ms-wmv']:
            # Используем временный файл для сохранения загруженного видео
            with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()  # Обеспечиваем запись всех данных на диск

                # Проверьте длительность видео
                clip = VideoFileClip(temp_file.name)
                duration = clip.duration

                if duration > max_duration:
                    raise forms.ValidationError(f"Длительность видео не должна превышать {max_duration} секунд.")

        return file


class DeleteMediaFileForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
