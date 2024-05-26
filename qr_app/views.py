import os
import qrcode
import random
import string
from PIL import Image
from moviepy.editor import VideoFileClip
import mimetypes
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from io import BytesIO
from qr_app.models import Postcard
from qr_app.forms import MediaFileForm, DeleteMediaFileForm


def generate_random_password(length=11):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def generate_qr_code_image(request, uuid):
    # Получение записи пароля по UUID
    password_entry = get_object_or_404(Postcard, uuid=uuid)

    # Генерация URL-адреса
    url = request.build_absolute_uri(f'/loveyou/{password_entry.uuid}/')

    # Генерация QR-кода
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')


def generate_qr_code(request):
    random_password = generate_random_password()
    password_entry = Postcard.objects.create(password=random_password)
    context = {
        'password': random_password,
        'password_entry': password_entry,
    }
    return render(request, 'qr_code.html', context)


def compress_image(image_path, output_path, quality=85):
    """
    Сжимает изображение и сохраняет его в указанном пути с заданным качеством.
    """
    try:
        with Image.open(image_path) as img:
            img.save(output_path, 'JPEG', quality=quality)
    except Exception as e:
        print(f"Error compressing image: {e}")


def compress_video(video_path, output_path, reduction_percentage=50):
    """
    Сжимает видео, уменьшая его размер на заданный процент, и сохраняет его в указанном пути.
    """
    try:
        clip = VideoFileClip(video_path)

        # Получаем исходный размер видео
        original_size = os.path.getsize(video_path)  # размер видео в байтах
        target_size = original_size * (1 - reduction_percentage / 100)  # целевой размер в байтах

        # Продолжительность видео в секундах
        duration = clip.duration

        # Целевой битрейт в битах в секунду
        target_bitrate = (target_size * 8) / duration  # битрейт в битах

        # Параметры кодирования
        codec = 'libx264'
        preset = 'slow'
        audio_bitrate = '128k'

        clip.write_videofile(
            output_path,
            codec=codec,
            bitrate=f"{int(target_bitrate / 1000)}k",  # битрейт в килобитах
            audio_codec='aac',
            audio_bitrate=audio_bitrate,
            preset=preset
        )
        print(f"Video compressed to: {output_path}")
    except Exception as e:
        print(f"Error compressing video: {e}")


def compress_media(file_path, media_type):
    """
    Определяет тип медиафайла и сжимает его в зависимости от типа (изображение или видео).
    """
    compressed_path = os.path.join(settings.MEDIA_ROOT, 'c_media_files', os.path.basename(file_path))
    try:
        if media_type == 'image':
            compress_image(file_path, compressed_path)
        elif media_type == 'video':
            compress_video(file_path, compressed_path)
        else:
            raise ValueError("Unsupported media type")

        if os.path.exists(compressed_path):
            os.remove(file_path)
        return compressed_path
    except Exception as e:
        print(f"Error compressing media: {e}")
        return None


def postcard_detail(request, uuid):
    """
    Обрабатывает запросы к странице подробностей открытки, включая добавление и удаление медиафайлов.
    """
    postcard = get_object_or_404(Postcard, uuid=uuid)
    media_file = getattr(postcard, 'media_file', None)

    add_form = MediaFileForm()
    delete_form = DeleteMediaFileForm()

    if request.method == 'POST':
        password = request.POST.get('password')

        if 'add_photo' in request.POST:
            add_form = MediaFileForm(request.POST, request.FILES)
            if add_form.is_valid():
                if password == postcard.password:
                    media_file = add_form.save(commit=False)
                    media_file.postcard = postcard
                    media_file.save()

                    mime_type, _ = mimetypes.guess_type(media_file.file.path)
                    media_type = mime_type.split('/')[0] if mime_type else None

                    if media_type in ['image', 'video']:
                        compressed_path = compress_media(media_file.file.path, media_type)
                        if compressed_path:
                            relative_compressed_path = os.path.relpath(compressed_path, settings.MEDIA_ROOT)
                            media_file.file.name = relative_compressed_path.replace('\\', '/')  # для корректного отображения в URL
                            media_file.save()
                            return redirect('postcard_detail', uuid=uuid)
                        else:
                            return HttpResponseForbidden('Error compressing media file')
                    else:
                        return HttpResponseForbidden('Unsupported media type')
                else:
                    return HttpResponseForbidden('Incorrect password')
            else:
                print(add_form.errors)

        elif 'delete_photo' in request.POST:
            delete_form = DeleteMediaFileForm(request.POST)
            if delete_form.is_valid():
                if password == postcard.password:
                    if media_file:
                        media_file.delete()
                        return redirect('postcard_detail', uuid=uuid)
                else:
                    return HttpResponseForbidden('Incorrect password')

    context = {
        'postcard': postcard,
        'media_file': media_file,
        'add_form': add_form,
        'delete_form': delete_form,
    }
    return render(request, 'postcard_detail.html', context)