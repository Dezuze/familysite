from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from news.models import Post, Media
from families.models import FamilyMember

class Command(BaseCommand):
    help = 'Seed dummy news and events'

    def handle(self, *args, **options):
        Post.objects.all().delete()
        Media.objects.all().delete()
        
        creators = list(FamilyMember.objects.filter(user_account__isnull=False))
        if not creators:
            self.stdout.write(self.style.ERROR('No linked family members found for creators.'))
            return

        # Seed Events (Upcoming & Past)
        events_data = [
            ("Annual Kudumbayogam 2026", "Join us for our annual family gathering. Lunch will be served.", 30),
            ("Easter Celebration", "Family prayer and dinner at the ancestral home.", 60),
            ("Youth Meetup", "A generic meetup for the youth wing.", -10), # Past
            ("Christmas Carol Rounds", "Carols visiting every house in the branch.", -40), # Past
        ]

        for title, desc, days_offset in events_data:
            creator = random.choice(creators)
            event_date = timezone.now() + timedelta(days=days_offset)
            post = Post.objects.create(
                creator=creator,
                post_type='event',
                title=title,
                description=desc,
                event_date=event_date
            )
            # Add dummy media
            Media.objects.create(
                uploader=creator,
                post=post,
                media_type='image',
                # using a placeholder or existing file path logic?
                # For now, leaving empty or relying on frontend placeholder if null
                # Or set a dummy path if you have seed images.
                # media_url='news/dummy_event.jpg' 
            )

        # Seed News
        news_data = [
            ("Congratulations to Sarah!", "Sarah graduated with honors from MG University."),
            ("New Branch Committee Elected", "The new committee members for 2026 have been selected."),
            ("Obituary: John Doe", "With deep grief we inform the passing of..."),
        ]

        for title, desc in news_data:
            creator = random.choice(creators)
            post = Post.objects.create(
                creator=creator,
                post_type='news',
                title=title,
                description=desc
            )
            Media.objects.create(
                uploader=creator,
                post=post,
                media_type='image'
            )

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(events_data)} events and {len(news_data)} news items.'))
