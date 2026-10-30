import time
import logging
from datetime import datetime, date
from django.core.management.base import BaseCommand
from news.services.daily_posters import ensure_daily_posters, run_daily_poster_generation

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Runs a continuous background daemon that automatically generates daily posters every day."

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=3600,
            help="Polling interval in seconds (default: 3600s / 1 hour)."
        )
        parser.add_argument(
            '--run-now',
            action='store_true',
            help="Immediately run poster generation on startup."
        )

    def handle(self, *args, **options):
        interval = options['interval']
        self.stdout.write(self.style.SUCCESS(f"[*] Starting daily poster scheduler daemon (Interval: {interval}s)..."))

        # Run immediately on daemon startup if requested
        if options.get('run_now', True):
            self.stdout.write("[*] Running initial check for today's posters...")
            res = run_daily_poster_generation(target_date=date.today())
            self.stdout.write(f"[*] Initial check complete: Created {res['created']}, Skipped {res['skipped']}")

        last_checked_day = date.today()

        while True:
            try:
                current_day = date.today()
                if current_day != last_checked_day:
                    self.stdout.write(self.style.NOTICE(f"[*] Date change detected: {current_day.isoformat()}. Generating posters..."))
                    res = run_daily_poster_generation(target_date=current_day)
                    self.stdout.write(self.style.SUCCESS(f"[+] Created {res['created']}, Skipped {res['skipped']}."))
                    last_checked_day = current_day
                else:
                    # Also ensure via cache in case it was missed
                    ensure_daily_posters()

                time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("[-] Scheduler daemon stopped by user."))
                break
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"[!] Scheduler loop error: {e}"))
                time.sleep(60)

