import base64
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def inline_logo():
    # Replace this path with your actual image path in your media folder or static
    logo_path = settings.BASE_DIR / 'static' / 'images' / 'logo.png'
    
    try:
        with open(logo_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_image}"
    except FileNotFoundError:
        return ""  # Return an empty string if the image is not found
