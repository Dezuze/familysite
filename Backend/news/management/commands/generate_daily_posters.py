from datetime import datetime, date
from django.core.management.base import BaseCommand
from news.services.daily_posters import run_daily_poster_generation

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

        res = run_daily_poster_generation(target_date=target_date, force=force, dry_run=dry_run)

        if res['status'] == 'no_events':
            self.stdout.write(self.style.SUCCESS(f"[+] No birthdays, wedding anniversaries, or death anniversaries found for {target_date}."))
            return

        if dry_run:
            events = res.get('events', [])
            self.stdout.write(self.style.NOTICE(f"[+] Found {len(events)} matching event(s):"))
            for idx, ev in enumerate(events, 1):
                safe_title = ev['title'].encode('ascii', 'replace').decode('ascii')
                self.stdout.write(f"  {idx}. [{ev['event_type'].upper()}] {ev['member'].name} - {safe_title}")
            self.stdout.write(self.style.SUCCESS("[*] Dry run complete. No posts or poster images were created."))
            return

        for skipped in res.get('skipped_posts', []):
            safe_title = skipped['title'].encode('ascii', 'replace').decode('ascii')
            self.stdout.write(self.style.WARNING(f"  [-] Skipped '{safe_title}': already generated (Post #{skipped['post_id']}). Use --force to override."))

        for created in res.get('created_posts', []):
            safe_title = created['title'].encode('ascii', 'replace').decode('ascii')
            self.stdout.write(self.style.SUCCESS(f"  [+] Generated poster & created Post #{created['post_id']} ({created['media_path']})"))

        self.stdout.write(self.style.SUCCESS(f"\n[Complete] Successfully created {res['created']} poster post(s), skipped {res['skipped']} existing."))
