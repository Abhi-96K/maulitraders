import segno
from PIL import Image, ImageDraw
import io
from django.conf import settings
import os

def generate_attractive_qr(data):
    """
    Generates a high-quality, rounded QR code with an embedded logo.
    Returns the image data as a Base64 string (or bytes) suitable for data URI.
    """
    # 1. Generate QR Matrix
    qr = segno.make(data, error='h')
    
    # 2. Settings
    module_size = 20 # Pixels per module (high res for printing)
    border = 2 # Modules
    theme_color = "#1a365d" # Mauli Traders Navy
    bg_color = "white"
    
    # Calculate Dimensions based on actual matrix
    matrix_width = len(qr.matrix)
    img_size = (matrix_width + (border * 2)) * module_size
    
    # 3. Create Canvas
    img = Image.new("RGBA", (img_size, img_size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 4. Draw Rounded Modules
    # qr.matrix_iter returns (row, col, is_dark)
    # 4. Draw Rounded Modules
    # Iterate manually over the matrix to ensure we catch all dark modules
    matrix = qr.matrix
    for r, row in enumerate(matrix):
        for c, is_dark in enumerate(row):
            if is_dark:
                x = (c + border) * module_size
                y = (r + border) * module_size
                
                # Draw Circle (Ellipse)
                padding = 1 
                draw.ellipse(
                    [x + padding, y + padding, x + module_size - padding, y + module_size - padding],
                    fill=theme_color
                )

    # 5. Embed Logo
    try:
        logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo_v2.png')
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            
            # Trim transparent whitespace to ensure visual centering
            bbox = logo.getbbox()
            if bbox:
                logo = logo.crop(bbox)
            
            # Calculate Logo Size (cover approx 25% of QR)
            logo_max_size = int(img_size * 0.25)
            logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
            
            # Create white background for logo
            # Use max dimension to keep box square
            logo_bg_dim = max(logo.size) + 20 
            logo_bg = Image.new("RGBA", (logo_bg_dim, logo_bg_dim), "white")
            
            # Round corners of logo background
            mask = Image.new("L", (logo_bg_dim, logo_bg_dim), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle((0, 0, logo_bg_dim, logo_bg_dim), radius=15, fill=255)
            
            # Composite
            # Center logo on canvas
            pos_x = (img_size - logo.size[0]) // 2
            pos_y = (img_size - logo.size[1]) // 2
            
            # Center box on canvas
            box_x = (img_size - logo_bg_dim) // 2
            box_y = (img_size - logo_bg_dim) // 2
            
            # Draw white box first (to clear dots behind logo)
            box_x = (img_size - logo_bg_dim) // 2
            box_y = (img_size - logo_bg_dim) // 2
            
            # Simple rectangle clear if masking is too complex for simple PIL usage
            draw.rounded_rectangle(
                [box_x, box_y, box_x + logo_bg_dim, box_y + logo_bg_dim],
                radius=20,
                fill="white"
            )
            
            # Paste Logo
            img.paste(logo, (pos_x, pos_y), logo)
            
    except Exception as e:
        print(f"Error embedding logo: {e}")
        # Continue without logo if fails

    # 6. Save to Buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()