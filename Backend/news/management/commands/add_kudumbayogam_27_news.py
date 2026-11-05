import os
from datetime import datetime, timezone as dt_timezone
from django.conf import settings
from django.core.management.base import BaseCommand
from families.models import FamilyMember
from news.models import Post, Media


NEWS_TITLE = "കൊല്ലംപറമ്പിൽ കുടുംബയോഗം 27ാം മത് വാർഷികാഘോഷം"

NEWS_DESCRIPTION = """കൊല്ലംപറമ്പിൽ കുടുംബയോഗം 27ാം മത് വാർഷികാഘോഷം 2026 ജനുവരി 24ന് കുളത്തമ്മാക്കൽ ശ്രീ കോരുള ഐസക്ക് ൻ്റെ ഭവനങ്കണത്തിൽ നടന്നു.

സമ്മേളനം ബഹു. MLA Sri. Chandy Oommen ഉദ്ഘാടനം ചെയ്തു.
വർക്കിംഗ് പ്രസിഡൻ്റ് ശ്രീ. കെ.എ. അന്ത്രയോസ് അയക്ഷത വഹിച്ചു. സെക്രട്ടറി ശ്രീ. പ്രവീൺ മാണി വാർഷിക റിപ്പോർട്ടും കണക്കും അവതരിപ്പിച്ചു..

കലാപരിപാടികൾക്ക് ശ്രീ. അനീഷ് നേതൃത്വം നൽകി.
യോഗത്തിൽ ആദ്യമായി ബൈബിൾ ക്വിസ് Dr. Santra Merin Saju അവതരിപ്പിച്ചു.

കാഥികനും, സാഹിത്യകാരനും, ശ്രീ കോട്ടയം ബാബുരാജ് ൻ്റെ നർമ്മ സംഭാഷണം ഉണ്ടായിരുന്നു.  
ഫാ. തോമസ് വേങ്കടത്ത് കോർ എപ്പിസ്ക്കോപ്പ മുഖ്യ പ്രഭാഷണവും, പാമ്പാടി പഞ്ചായത്ത് പ്രസിഡൻ്റ് 
അഡ്വ സിജു കെ. ഐസക്ക്, വാർഡ് മെമ്പർ ശ്രീമതി. രജനി ED, Fr കുറിയാക്കോസ് കുറിച്ചിമല,
ശ്രീ. പി.സി. ചാക്കോ,
ശ്രീ. റ്റി.എം. മാത്യു എന്നിവർ ആശംസകൾ അർപ്പിച്ചു..

ജൂബിലേറിയ ൻമാരെയും ഉന്നതവിജയം, ജോലി ലഭിച്ചവരെയും, newly married couples, parents of new born baby എന്നിവരെ ആദരിച്ചു."""

NEWS_LOCATION = "കുളത്തമ്മാക്കൽ ശ്രീ കോരുള ഐസക്ക് ൻ്റെ ഭവനങ്കണം"


class Command(BaseCommand):
    help = "Creates or updates the 27th Annual Kudumbayogam Celebration news post and links its photos."

    def handle(self, *args, **options):
        creator = (
            FamilyMember.objects.filter(name__icontains="Praveen Mani").first()
            or FamilyMember.objects.filter(is_deceased=False).first()
            or FamilyMember.objects.first()
        )
        if not creator:
            self.stderr.write(self.style.ERROR("No FamilyMember found to assign as creator."))
            return

        event_dt = datetime(2026, 1, 24, 10, 0, tzinfo=dt_timezone.utc)

        post, created = Post.objects.update_or_create(
            title=NEWS_TITLE,
            defaults={
                "creator": creator,
                "post_type": "news",
                "description": NEWS_DESCRIPTION,
                "event_date": event_dt,
                "location": NEWS_LOCATION,
                "is_kudumbayogam": True,
                "is_auto_generated": False,
                "visibility": "public",
            },
        )

        media_subdir = "media_gallery/kudumbayogam_27"
        abs_media_dir = os.path.join(settings.MEDIA_ROOT, "media_gallery", "kudumbayogam_27")

        if not os.path.isdir(abs_media_dir):
            self.stderr.write(self.style.WARNING(f"Media folder not found at {abs_media_dir}"))
            return

        image_files = sorted(
            f for f in os.listdir(abs_media_dir)
            if f.lower().endswith((".jpeg", ".jpg", ".png", ".webp"))
        )

        # Clear existing media records for this post and re-attach in order
        post.media.all().delete()

        attached_count = 0
        for idx, fname in enumerate(image_files, 1):
            rel_path = f"{media_subdir}/{fname}"
            Media.objects.create(
                uploader=creator,
                post=post,
                media_url=rel_path,
                caption=f"{NEWS_TITLE} - Photo {idx}",
                media_type="image",
                is_personal_gallery=False,
            )
            attached_count += 1

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"[+] {action} News Post #{post.id} with {attached_count} image(s)."
            )
        )

