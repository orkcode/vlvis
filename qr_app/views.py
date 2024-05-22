import os
import qrcode
import random
import string
import mimetypes
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from io import BytesIO
from qr_app.models import Postcard
from qr_app.forms import MediaFileForm, DeleteMediaFileForm
from qr_app.utils import compress_image, compress_video


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


def compress_media(file_path, media_type):
    compressed_path = os.path.join(settings.MEDIA_ROOT, 'c_media_files', os.path.basename(file_path))
    if media_type == 'image':
        compress_image(file_path, compressed_path)
    elif media_type == 'video':
        compress_video(file_path, compressed_path)
    return compressed_path


def postcard_detail(request, uuid):
    postcard = get_object_or_404(Postcard, uuid=uuid)
    media_file = getattr(postcard, 'media_file', None)

    add_form = MediaFileForm()
    delete_form = DeleteMediaFileForm()

    if request.method == 'POST':
        if 'add_photo' in request.POST:
            form = MediaFileForm(request.POST, request.FILES)
            if form.is_valid():
                if request.POST.get('password') == postcard.password:
                    media_file = form.save(commit=False)
                    media_file.postcard = postcard
                    media_file.save()

                    mime_type, _ = mimetypes.guess_type(media_file.file.path)
                    media_type = mime_type.split('/')[0] if mime_type else None

                    if media_type in ['image', 'video']:
                        compressed_path = compress_media(media_file.file.path, media_type)
                        media_file.file.name = os.path.join('media_files', os.path.basename(compressed_path))
                        media_file.save()
                        return redirect('postcard_detail', uuid=uuid)
                    else:
                        return HttpResponseForbidden('Unsupported media type')
                else:
                    return HttpResponseForbidden('Incorrect password')
            else:
                print(form.errors)

        elif 'delete_photo' in request.POST:
            form = DeleteMediaFileForm(request.POST)
            if form.is_valid():
                if request.POST.get('password') == postcard.password:
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