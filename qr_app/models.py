from django.db import models
import uuid
import os


class Postcard(models.Model):
    password = models.CharField(max_length=128)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return str(self.uuid)


class MediaFile(models.Model):
    postcard = models.OneToOneField(Postcard, on_delete=models.CASCADE, related_name='media_file')
    file = models.FileField(upload_to='media_files/')

    def is_video(self):
        _, ext = os.path.splitext(self.file.name)
        return ext.lower() in ['.mp4', '.mov', '.avi', '.wmv']

    def is_image(self):
        _, ext = os.path.splitext(self.file.name)
        return ext.lower() in ['.jpg', '.jpeg', '.png', '.gif']

    def __str__(self):
        return f"Media for {self.postcard.uuid}"