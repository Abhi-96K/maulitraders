
import os
import django
import cloudinary.uploader
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maulitraders.settings')
django.setup()

from django.conf import settings

# Configure Cloudinary (it should pick up from settings, but let's be explicit if needed)
# settings.CLOUDINARY_STORAGE handles django-cloudinary-storage, but we are using cloudinary lib directly here.
# We need to configure it globally for uploader to work.
import cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
)

MEDIA_ROOT = settings.MEDIA_ROOT

def upload_files():
    print(f"Scanning {MEDIA_ROOT} for files...")
    count = 0
    for root, dirs, files in os.walk(MEDIA_ROOT):
        for file in files:
            if file.startswith('.'):
                continue
            
            file_path = os.path.join(root, file)
            # Calculate relative path for public_id (e.g., products/myimage.jpg)
            relative_path = os.path.relpath(file_path, MEDIA_ROOT)
            
            # Cloudinary public_id should not have extension? 
            # Actually, standard Django storage usually keeps extension in name or uses it to determine format.
            # But specific public_id usually excludes extension if using 'use_filename' etc.
            # However, if we want the URL to match what's in DB (which includes extension usually?),
            # wait. DB stores "products/img.jpg".
            # If we upload with public_id="products/img.jpg", Cloudinary URL might be .../products/img.jpg
            # Let's try to upload with use_filename=True, unique_filename=False, folder=dirname?
            
            # Better approach: public_id = relative_path without extension?
            # Or just public_id = relative_path.
            # Cloudinary adds extension by default to delivery URL.
            # If DB says "products/img.jpg", and we access it via MediaCloudinaryStorage, 
            # it constructs URL based on that name.
            # Let's clean the public_id.
            
            # Strategy: public_id = relative_path (minus extension? No, let's keep it simple)
            # If I upload "products/img.jpg" as public_id "products/img", Cloudinary delivers "products/img.jpg".
            
            public_id = os.path.splitext(relative_path)[0]
            
            print(f"Uploading {relative_path} as {public_id}...")
            try:
                cloudinary.uploader.upload(file_path, public_id=public_id, overwrite=True, resource_type="auto")
                count += 1
            except Exception as e:
                print(f"Failed to upload {file_path}: {e}")

    print(f"Successfully uploaded {count} files.")

if __name__ == "__main__":
    upload_files()
