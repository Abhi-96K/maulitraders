from io import BytesIO
from django.core.files import File
from PIL import Image

def compress_image(image, quality=70, max_size=(800, 800)):
    """
    Compresses the given image file using Pillow.
    - Resizes to max_size (preserving aspect ratio).
    - Converts to RGB.
    - Saves as JPEG with reduced quality.
    """
    img = Image.open(image)
    
    # Convert to RGB if necessary (e.g., for PNGs with transparency)
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    # Resize if too large
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save to BytesIO buffer
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    return File(output, name=image.name.split('.')[0] + '.jpg')
