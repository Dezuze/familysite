import sys
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.models import Post, Media
from families.models import FamilyMember
from news.services.anniversary_detector import AnniversaryDetector
from news.services.poster_generator import PosterGenerator

class Command(BaseCommand):
    help = "Generates automated celebration posters for birthdays, wedding anniversaries, and death anniversaries, and publishes them to the News & Events feed."

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help="Target date in YYYY-MM-DD format (defaults to today's date)."
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Scan and list events without creating posters or database records."
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help="Force creation even if a post for this event already exists today."
        )

    def handle(self, *args, **options):
        # Determine target date
        date_arg = options.get('date')
        if date_arg:
            try:
                target_date = datetime.strptime(date_arg, "%Y-%m-%d").date()
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Invalid date format '{date_arg}'. Expected YYYY-MM-DD."))
                return
        else:
            target_date = date.today()

        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        self.stdout.write(self.style.NOTICE(f"[*] Scanning events for date: {target_date.strftime('%B %d, %Y')} (Dry Run: {dry_run})"))

        events = AnniversaryDetector.get_events_for_date(target_date)

        if not events:
            self.stdout.write(self.style.SUCCESS(f"[+] No birthdays, wedding anniversaries, or death anniversaries found for {target_date}."))
            return

        self.stdout.write(self.style.NOTICE(f"[+] Found {len(events)} matching event(s):"))
        for idx, ev in enumerate(events, 1):
            safe_title = ev['title'].encode('ascii', 'replace').decode('ascii')
            self.stdout.write(f"  {idx}. [{ev['event_type'].upper()}] {ev['member'].name} - {safe_title}")

        if dry_run:
            self.stdout.write(self.style.SUCCESS("[*] Dry run complete. No posts or poster images were created."))
            return

        # Default creator fallback
        default_creator = FamilyMember.objects.filter(is_deceased=False).first()
        if not default_creator:
            default_creator = FamilyMember.objects.first()

        created_count = 0
        skipped_count = 0

        for ev in events:
            member = ev['member']
            event_type = ev['event_type']
            title = ev['title']
            description = ev['description']
            safe_title = title.encode('ascii', 'replace').decode('ascii')

            # Duplicate prevention check (ensure not already posted for this year)
            existing_post = Post.objects.filter(
                is_auto_generated=True,
                title=title,
                created_at__year__in=[target_date.year, timezone.now().year]
            ).first()

            if existing_post and not force:
                self.stdout.write(self.style.WARNING(f"  [-] Skipped '{safe_title}': already generated (Post #{existing_post.id}). Use --force to override."))
                skipped_count += 1
                continue

            try:
                # 1. Generate poster image using Pillow service
                custom_date_str = target_date.strftime("%B %d, %Y")
                relative_media_path = PosterGenerator.generate_poster(
                    member=member,
                    event_type=event_type,
                    spouse=ev.get('spouse'),
                    custom_date_str=custom_date_str
                )

                # 2. Determine post creator
                creator = member if not member.is_deceased else default_creator

                # 3. Create News Post
                post = Post.objects.create(
                    creator=creator,
                    post_type='news',
                    title=title,
                    description=description,
                    event_date=timezone.now(),
                    is_auto_generated=True,
                    visibility='public'
                )

                # 4. Attach Media item
                media = Media.objects.create(
                    uploader=creator,
                    post=post,
                    media_url=relative_media_path,
                    caption=title,
                    media_type='image'
                )

                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  [+] Generated poster & created Post #{post.id} for {member.name} ({relative_media_path})"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  [!] Failed to generate poster for {member.name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n[Complete] Successfully created {created_count} poster post(s), skipped {skipped_count} existing."))
