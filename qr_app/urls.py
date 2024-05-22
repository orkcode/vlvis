from django.urls import path
from qr_app.views import generate_qr_code, postcard_detail, generate_qr_code_image

urlpatterns = [
    path('', generate_qr_code, name='generate_qr_code'),
    path('loveyou/<uuid:uuid>/', postcard_detail, name='postcard_detail'),
    path('qr-code/<uuid:uuid>/', generate_qr_code_image, name='generate_qr_code_image'),
]

