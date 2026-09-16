import os
from io import BytesIO
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

class PosterGenerator:
    """
    Generates high-resolution celebration and remembrance posters (1080x1080)
    for members' birthdays, wedding anniversaries, and death anniversaries.
    """

    TEMPLATE_FILES = {
        'birthday': 'birthday_template.png',
        'wedding_anniversary': 'wedding_anniversary_template.png',
        'death_anniversary': 'death_anniversary_template.png',
    }

    # Center coordinates of the circular portrait portal on templates
    CIRCLE_CENTER = (540, 440)
    CIRCLE_RADIUS = 180

    @classmethod
    def get_font(cls, size, bold=False):
        font_names = ['georgia.ttf', 'arial.ttf', 'times.ttf', 'DejaVuSans.ttf']
        for name in font_names:
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        return ImageFont.load_default()

    @classmethod
    def smart_face_crop(cls, img, diameter):
        """
        Attempts to detect a face using OpenCV. If found, crops a square around it
        with some padding. If not found, falls back to ImageOps.fit center crop.
        """
        try:
            import cv2
            import numpy as np
            
            # Convert PIL image to OpenCV format (BGR)
            cv_img = np.array(img.convert('RGB'))
            cv_img = cv_img[:, :, ::-1].copy()
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            # Histogram Equalization for better contrast
            gray = cv2.equalizeHist(gray)
            
            # Load Haar Cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) > 0:
                # Find the largest face by area
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                x, y, w, h = faces[0]
                
                # Face center
                cx = x + w // 2
                cy = y + h // 2
                
                # Padding multiplier
                crop_size = int(max(w, h) * 1.8)
                
                # Shift Y center slightly down (which means higher y value) to include more shoulders
                cy = cy + int(h * 0.15)
                
                half_size = crop_size // 2
                
                x1 = max(0, cx - half_size)
                y1 = max(0, cy - half_size)
                x2 = min(img.width, cx + half_size)
                y2 = min(img.height, cy + half_size)
                
                # Make it a perfect square
                actual_w = x2 - x1
                actual_h = y2 - y1
                final_size = min(actual_w, actual_h)
                
                if actual_w > final_size:
                    diff = actual_w - final_size
                    x1 += diff // 2
                    x2 = x1 + final_size
                if actual_h > final_size:
                    diff = actual_h - final_size
                    y1 += diff // 2
                    y2 = y1 + final_size
                
                cropped = img.crop((x1, y1, x2, y2))
                return cropped.resize((diameter, diameter), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Face detection error: {e}")
            pass
            
        # Fallback to center crop
        return ImageOps.fit(img, (diameter, diameter), Image.Resampling.LANCZOS)

    @classmethod
    def create_circular_avatar(cls, image_path_or_file, diameter):
        """
        Loads an image, crops it to square (using smart face detection if possible),
        and applies a smooth circular mask.
        """
        try:
            img = Image.open(image_path_or_file).convert("RGBA")
        except Exception:
            return None

        # Fit into square without distortion (using face detection)
        fitted = cls.smart_face_crop(img, diameter)

        # Create smooth anti-aliased circular mask using 2x supersampling
        scale = 2
        mask_size = (diameter * scale, diameter * scale)
        mask = Image.new('L', mask_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, mask_size[0], mask_size[1]), fill=255)
        mask = mask.resize((diameter, diameter), Image.Resampling.LANCZOS)

        fitted.putalpha(mask)
        return fitted

    @classmethod
    def create_fallback_avatar(cls, name, diameter, event_type='birthday'):
        """
        Creates an aesthetic letter-avatar circle when member has no photo.
        """
        bg_colors = {
            'birthday': (24, 39, 75),
            'wedding_anniversary': (20, 50, 40),
            'death_anniversary': (30, 41, 59),
        }
        bg = bg_colors.get(event_type, (30, 41, 59))
        
        avatar = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
        draw = ImageDraw.Draw(avatar)
        draw.ellipse((0, 0, diameter, diameter), fill=bg)

        initial = (name.strip()[0] if name.strip() else 'K').upper()
        font = cls.get_font(int(diameter * 0.45), bold=True)
        draw.text((diameter / 2, diameter / 2 - 5), initial, fill=(212, 175, 55), font=font, anchor="mm")

        return avatar

    @classmethod
    def generate_poster(cls, member, event_type, spouse=None, custom_date_str=None):
        """
        Generates the poster and saves it to media/media_gallery/auto_posters/.
        Returns the relative media path (e.g. 'media_gallery/auto_posters/...').
        """
        template_name = cls.TEMPLATE_FILES.get(event_type, 'birthday_template.png')
        template_path = os.path.join(settings.MEDIA_ROOT, 'poster_templates', template_name)

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Poster template not found at {template_path}")

        poster = Image.open(template_path).convert("RGBA")
        
        # Ensure it's 1080x1350 natively
        final_w, final_h = 1080, 1350
        poster = ImageOps.fit(poster, (final_w, final_h), Image.Resampling.LANCZOS)
        
        draw = ImageDraw.Draw(poster)

        # Template-specific precise circle coordinates (cx, cy, r)
        coord_map = {
            'birthday': (540, 385, 235),
            'wedding_anniversary': (540, 420, 285),
            'death_anniversary': (540, 410, 260)
        }
        cx, cy, r = coord_map.get(event_type, (540, 400, 250))
        diameter = r * 2

        # 1. Process Member Avatar
        avatar = None
        if member.photo and hasattr(member.photo, 'path') and os.path.exists(member.photo.path):
            avatar = cls.create_circular_avatar(member.photo.path, diameter)
        
        if avatar is None:
            avatar = cls.create_fallback_avatar(member.name, diameter, event_type)

        # Paste avatar into center circle
        paste_x = cx - r
        paste_y = cy - r
        poster.paste(avatar, (paste_x, paste_y), avatar)

        # 2. Render Name with Dynamic Sizing
        display_name = member.name.strip()
        if event_type == 'wedding_anniversary' and spouse:
            display_name = f"{member.name} & {spouse.name}"

        # Adjust font size to ensure name fits inside 600px width
        max_name_width = 580
        font_size = 42 if len(display_name) <= 24 else 34
        if len(display_name) > 36:
            font_size = 28

        name_font = cls.get_font(font_size, bold=True)
        if event_type == 'death_anniversary':
            text_color = (100, 116, 139) # Slate 500
        else:
            text_color = (30, 41, 59) # Slate 800

        # Draw Event Title (Happy Birthday, etc)
        title_map = {
            'birthday': 'Happy Birthday',
            'wedding_anniversary': 'Happy Anniversary',
            'death_anniversary': 'In Loving Memory'
        }
        event_title = title_map.get(event_type, 'Special Occasion')
        title_font = cls.get_font(38, bold=False)
        title_color = (148, 163, 184) if event_type == 'death_anniversary' else (212, 175, 55) # Gold or soft slate
        
        # Position text relative to the bottom of the portrait circle
        circle_bottom = cy + r
        title_y = circle_bottom + 100
        draw.text((cx, title_y), event_title, fill=title_color, font=title_font, anchor="mm")

        # Draw member name centered in name banner area
        name_y = title_y + 100
        draw.text((cx, name_y), display_name, fill=text_color, font=name_font, anchor="mm")

        # 3. Render Subtitle / Branch / House Info (y ~ 820)
        sub_items = []
        if member.branch:
            sub_items.append(str(member.branch))
        elif member.family:
            sub_items.append(str(member.family.branch))
            
        if member.family_name:
            sub_items.append(str(member.family_name))

        if custom_date_str:
            sub_items.append(custom_date_str)

        sub_text = " • ".join(sub_items) if sub_items else "Kollamparampil Family"
        sub_font = cls.get_font(28)
        if event_type == 'death_anniversary':
            sub_color = (148, 163, 184)
        else:
            sub_color = (71, 85, 105)
        sub_y = name_y + 100
        draw.text((cx, sub_y), sub_text, fill=sub_color, font=sub_font, anchor="mm")

        # 4. Save to destination
        dest_dir = os.path.join(settings.MEDIA_ROOT, 'media_gallery', 'auto_posters')
        os.makedirs(dest_dir, exist_ok=True)

        clean_date = (custom_date_str or 'poster').replace(" ", "_").replace(",", "")
        filename = f"{event_type}_{member.id}_{clean_date}.jpg"
        dest_path = os.path.join(dest_dir, filename)

        # Convert back to RGB for crisp JPEG output
        rgb_poster = poster.convert("RGB")
        rgb_poster.save(dest_path, "JPEG", quality=92, optimize=True)

        # Return path relative to MEDIA_ROOT
        relative_path = os.path.join('media_gallery', 'auto_posters', filename).replace('\\', '/')
        return relative_path
