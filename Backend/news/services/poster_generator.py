import os
from io import BytesIO
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

class PosterGenerator:
    """
    Generates high-resolution celebration and remembrance posters (1080x1350)
    for members birthdays, wedding anniversaries, and death anniversaries.
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
    def detect_faces_robust(cls, img_pil):
        """
        Robust face detection that downscales high-res photos to prevent false positives
        from intricate background textures, then returns coordinates in original scale.
        """
        try:
            import cv2
            import numpy as np

            max_dim = max(img_pil.width, img_pil.height)
            scale = 1200.0 / max_dim if max_dim > 1200 else 1.0

            if scale < 1.0:
                small = img_pil.resize((int(img_pil.width * scale), int(img_pil.height * scale)), Image.Resampling.LANCZOS)
            else:
                small = img_pil

            cv_img = cv2.cvtColor(np.array(small.convert('RGB')), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=5, minSize=(35, 35))
            if len(faces) == 0:
                return []

            orig_faces = []
            for f in faces:
                orig_faces.append((int(f[0] / scale), int(f[1] / scale), int(f[2] / scale), int(f[3] / scale)))
            orig_faces.sort(key=lambda f: f[2] * f[3], reverse=True)
            return orig_faces
        except Exception as e:
            print(f"Face detection error: {e}")
            return []

    @classmethod
    def select_target_face(cls, img_pil, faces, member=None):
        """
        When multiple faces are detected in a solo member's portrait photo (e.g. couple photo
        uploaded to an individual profile):
        1. If the member has a spouse with a photo in the DB, compare candidate faces
           against the spouse's photo. The face matching the spouse is excluded so the
           member's own face is chosen.
        2. Uses gender and facial characteristics (lower-face texture / facial hair)
           to ensure a female member is matched to the female face and vice-versa.
        """
        if not faces or len(faces) <= 1 or not member:
            return faces[0] if faces else None

        top_faces = faces[:2]

        # 1. Spouse photo exclusion
        try:
            from families.models import Relationship
            sp_rel = Relationship.objects.filter(from_member=member, relation_type__iexact='SPOUSE').select_related('to_member').first()
            spouse = sp_rel.to_member if sp_rel else None
            if not spouse:
                sp_rel2 = Relationship.objects.filter(to_member=member, relation_type__iexact='SPOUSE').select_related('from_member').first()
                spouse = sp_rel2.from_member if sp_rel2 else None

            if spouse and spouse.photo and hasattr(spouse.photo, 'path') and os.path.exists(spouse.photo.path):
                import cv2
                import numpy as np
                img_sp = ImageOps.exif_transpose(Image.open(spouse.photo.path)).convert('RGB')
                sp_faces = cls.detect_faces_robust(img_sp)
                if sp_faces:
                    sx, sy, sw, sh = sp_faces[0]
                    sp_crop = cv2.resize(np.array(img_sp.crop((sx, sy, sx + sw, sy + sh))), (100, 100))
                    sp_gray = cv2.cvtColor(sp_crop, cv2.COLOR_RGB2GRAY)

                    scores = []
                    for (fx, fy, fw, fh) in top_faces:
                        fc = cv2.resize(np.array(img_pil.crop((fx, fy, fx + fw, fy + fh)).convert('RGB')), (100, 100))
                        fg = cv2.cvtColor(fc, cv2.COLOR_RGB2GRAY)
                        res = cv2.matchTemplate(fg, sp_gray, cv2.TM_CCOEFF_NORMED)
                        scores.append(res[0][0])

                    spouse_idx = int(np.argmax(scores))
                    if scores[spouse_idx] > 0.25:
                        member_idx = 1 - spouse_idx
                        return top_faces[member_idx]
        except Exception:
            pass

        # 2. Gender heuristic (lower-half brightness / beard presence)
        if hasattr(member, 'gender') and member.gender:
            try:
                import cv2
                import numpy as np
                lower_means = []
                for (fx, fy, fw, fh) in top_faces:
                    fc = cv2.resize(np.array(img_pil.crop((fx, fy, fx + fw, fy + fh)).convert('RGB')), (100, 100))
                    fg = cv2.cvtColor(fc, cv2.COLOR_RGB2GRAY)
                    lower_means.append(float(np.mean(fg[50:, :])))

                if member.gender.upper() == 'F':
                    best_idx = int(np.argmax(lower_means))
                    return top_faces[best_idx]
                elif member.gender.upper() == 'M':
                    best_idx = int(np.argmin(lower_means))
                    return top_faces[best_idx]
            except Exception:
                pass

        return top_faces[0]

    @classmethod
    def smart_face_crop(cls, img, diameter, member=None):
        """
        Attempts to detect a face using OpenCV. If multiple faces exist, selects the correct
        face for the specified member. Crops a square around it with generous padding.
        """
        faces = cls.detect_faces_robust(img)
        if len(faces) > 0:
            target_face = cls.select_target_face(img, faces, member)
            x, y, w, h = target_face
            cx = x + w // 2
            cy = y + h // 2

            crop_size = int(max(w, h) * 1.85)
            cy = cy + int(h * 0.15)  # Shift down slightly for shoulders

            half_size = crop_size // 2
            x1 = max(0, cx - half_size)
            y1 = max(0, cy - half_size)
            x2 = min(img.width, cx + half_size)
            y2 = min(img.height, cy + half_size)

            actual_s = min(x2 - x1, y2 - y1)
            cropped = img.crop((cx - actual_s // 2, cy - actual_s // 2, cx + actual_s // 2, cy + actual_s // 2))
            return cropped.resize((diameter, diameter), Image.Resampling.LANCZOS)

        return ImageOps.fit(img, (diameter, diameter), Image.Resampling.LANCZOS)

    @classmethod
    def crop_couple_faces(cls, img_pil, faces, diameter):
        """
        Crops a couple photo around both detected faces into a circular portrait.
        """
        top_faces = faces[:2]
        min_x = min(f[0] for f in top_faces)
        max_x = max(f[0] + f[2] for f in top_faces)
        min_y = min(f[1] for f in top_faces)
        max_y = max(f[1] + f[3] for f in top_faces)

        cx = (min_x + max_x) // 2
        cy = (min_y + max_y) // 2
        span_w = max_x - min_x
        span_h = max_y - min_y

        crop_size = int(max(span_w, span_h) * 2.15)
        cy = cy + int(span_h * 0.18)

        half = crop_size // 2
        x1 = max(0, cx - half)
        y1 = max(0, cy - half)
        x2 = min(img_pil.width, cx + half)
        y2 = min(img_pil.height, cy + half)

        actual_s = min(x2 - x1, y2 - y1)
        cropped = img_pil.crop((cx - actual_s // 2, cy - actual_s // 2, cx + actual_s // 2, cy + actual_s // 2))
        fitted = cropped.resize((diameter, diameter), Image.Resampling.LANCZOS)

        # Smooth circular mask using 2x supersampling
        scale = 2
        mask_size = (diameter * scale, diameter * scale)
        mask = Image.new('L', mask_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, mask_size[0], mask_size[1]), fill=255)
        mask = mask.resize((diameter, diameter), Image.Resampling.LANCZOS)

        fitted.putalpha(mask)
        return fitted

    @classmethod
    def create_circular_avatar(cls, image_path_or_file, diameter, member=None):
        """
        Loads an image, normalizes orientation with exif_transpose, crops it to square
        (using smart face detection with member targeting), and applies a smooth circular mask.
        """
        try:
            img = Image.open(image_path_or_file)
            img = ImageOps.exif_transpose(img).convert("RGBA")
        except Exception:
            return None

        # Fit into square without distortion (using member-aware face detection)
        fitted = cls.smart_face_crop(img, diameter, member=member)

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
    def create_couple_avatar(cls, member, spouse, diameter):
        """
        Creates a dual-face circular avatar for wedding anniversaries:
        - If either member or spouse has a photo with 2+ faces (e.g. wedding/couple photo),
          it frames both faces together into the main circular portal.
        - If both have solo individual photos, it creates dual cameo circles side-by-side
          with refined gold borders inside the portal.
        - Falls back gracefully to single photo or initial avatars if photos are missing.
        """
        p1 = member.photo.path if (member and member.photo and hasattr(member.photo, 'path') and os.path.exists(member.photo.path)) else None
        p2 = spouse.photo.path if (spouse and spouse.photo and hasattr(spouse.photo, 'path') and os.path.exists(spouse.photo.path)) else None

        img1, faces1 = None, []
        if p1:
            try:
                img1 = ImageOps.exif_transpose(Image.open(p1)).convert("RGBA")
                faces1 = cls.detect_faces_robust(img1)
            except Exception:
                img1 = None

        img2, faces2 = None, []
        if p2:
            try:
                img2 = ImageOps.exif_transpose(Image.open(p2)).convert("RGBA")
                faces2 = cls.detect_faces_robust(img2)
            except Exception:
                img2 = None

        # Case 1: Photo 1 already has 2+ faces (couple photo)
        if img1 and len(faces1) >= 2:
            return cls.crop_couple_faces(img1, faces1, diameter)

        # Case 2: Photo 2 already has 2+ faces (couple photo)
        if img2 and len(faces2) >= 2:
            return cls.crop_couple_faces(img2, faces2, diameter)

        # Case 3: Both have solo individual photos (or one photo + spouse fallback)
        circle_d = int(diameter * 0.60)
        circle_r = circle_d // 2
        offset_x = int(diameter * 0.17)

        def make_bordered_circle(img_obj, fallback_name, target_mem):
            if img_obj:
                av = cls.smart_face_crop(img_obj, circle_d, member=target_mem)
                mask = Image.new('L', (circle_d * 2, circle_d * 2), 0)
                draw_m = ImageDraw.Draw(mask)
                draw_m.ellipse((0, 0, circle_d * 2, circle_d * 2), fill=255)
                mask = mask.resize((circle_d, circle_d), Image.Resampling.LANCZOS)
                av.putalpha(mask)
            else:
                av = cls.create_fallback_avatar(fallback_name, circle_d, 'wedding_anniversary')

            bordered = av.copy()
            draw_b = ImageDraw.Draw(bordered)
            border_w = 5
            gold_color = (212, 175, 55, 255)
            draw_b.ellipse((border_w // 2, border_w // 2, circle_d - border_w // 2 - 1, circle_d - border_w // 2 - 1), outline=gold_color, width=border_w)
            return bordered

        left_circle = make_bordered_circle(img1, member.name if member else 'Husband', member)
        right_circle = make_bordered_circle(img2, spouse.name if spouse else 'Wife', spouse)

        composite = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
        cx = diameter // 2
        cy = diameter // 2

        # Paste left circle
        composite.paste(left_circle, (cx - offset_x - circle_r, cy - circle_r), left_circle)
        # Paste right circle
        composite.paste(right_circle, (cx + offset_x - circle_r, cy - circle_r), right_circle)

        return composite

    @classmethod
    def generate_poster(cls, member, event_type, spouse=None, custom_date_str=None):
        """
        Generates the poster and saves it to media/media_gallery/auto_posters/.
        Returns the relative media path (e.g. 'media_gallery/auto_posters/...').
        """
        template_name = cls.TEMPLATE_FILES.get(event_type, 'birthday_template.png')
        template_path = os.path.join(settings.BASE_DIR, 'news', 'poster_templates', template_name)

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Poster template not found at {template_path}")

        poster = Image.open(template_path).convert("RGBA")

        # Ensure it is 1080x1350 natively
        final_w, final_h = 1080, 1350
        poster = ImageOps.fit(poster, (final_w, final_h), Image.Resampling.LANCZOS)

        draw = ImageDraw.Draw(poster)

        # Template-specific precise circle coordinates (cx, cy, r)
        coord_map = {
            'birthday': (540, 382, 235),
            'wedding_anniversary': (540, 418, 288),
            'death_anniversary': (547, 425, 259)
        }
        cx, cy, r = coord_map.get(event_type, (540, 400, 250))
        diameter = r * 2

        # 1. Process Member Avatar(s)
        if event_type == 'wedding_anniversary' and spouse:
            avatar = cls.create_couple_avatar(member, spouse, diameter)
        else:
            avatar = None
            if member.photo and hasattr(member.photo, 'path') and os.path.exists(member.photo.path):
                avatar = cls.create_circular_avatar(member.photo.path, diameter, member=member)

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
        font_size = 42 if len(display_name) <= 24 else 34
        if len(display_name) > 36:
            font_size = 28

        name_font = cls.get_font(font_size, bold=True)
        if event_type == 'death_anniversary':
            text_color = (71, 85, 105) # Slate 600
        else:
            text_color = (30, 41, 59) # Slate 800

        # Draw Event Title (Happy Birthday, Happy Anniversary, etc)
        title_map = {
            'birthday': 'Happy Birthday',
            'wedding_anniversary': 'Happy Anniversary',
            'death_anniversary': 'In Loving Memory'
        }
        event_title = title_map.get(event_type, 'Special Occasion')
        title_font = cls.get_font(38, bold=False)
        title_color = (100, 116, 139) if event_type == 'death_anniversary' else (205, 160, 40) # Warm Gold / soft slate

        # Position text with template-aware spacing to avoid graphics (e.g. wedding rings, laurels)
        if event_type == 'wedding_anniversary':
            title_y = 860
            name_y = 930
            sub_y = 995
        elif event_type == 'death_anniversary':
            title_y = 810
            name_y = 880
            sub_y = 945
        else:
            circle_bottom = cy + r
            title_y = circle_bottom + 85
            name_y = title_y + 80
            sub_y = name_y + 70

        draw.text((cx, title_y), event_title, fill=title_color, font=title_font, anchor="mm")

        # Draw member name centered in name banner area
        draw.text((cx, name_y), display_name, fill=text_color, font=name_font, anchor="mm")

        # 3. Render Subtitle / Branch / House Info
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
            sub_color = (100, 116, 139)
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
