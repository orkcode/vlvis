import base64
from django import template

register = template.Library()

@register.filter(name='base64')
def base64_encode(image):
    return base64.b64encode(image).decode('ascii')