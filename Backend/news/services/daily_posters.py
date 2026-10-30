import logging
from datetime import date
from django.utils import timezone
from django.core.cache import cache
from families.models import FamilyMember
from news.models import Post, Media
from news.services.anniversary_detector import AnniversaryDetector
from news.services.poster_generator import PosterGenerator

logger = logging.getLogger(__name__)

def run_daily_poster_generation(target_date=None, force=False, dry_run=False):
    """
    Scans family tree for birthdays, wedding anniversaries, and death anniversaries
    on target_date (defaults to today). Generates celebration posters and publishes
    them as news posts in the database.
    """
    if target_date is None:
        target_date = date.today()

    events = AnniversaryDetector.get_events_for_date(target_date)
    if not events:
        return {'status': 'no_events', 'created': 0, 'skipped': 0, 'events': []}

    if dry_run:
        return {'status': 'dry_run', 'created': 0, 'skipped': 0, 'events': events}

    default_creator = FamilyMember.objects.filter(is_deceased=False).first()
    if not default_creator:
        default_creator = FamilyMember.objects.first()

    created_posts = []
    skipped_posts = []

    for ev in events:
        member = ev['member']
        event_type = ev['event_type']
        title = ev['title']
        description = ev['description']

        # Duplicate prevention check (ensure not already posted for this year)
        existing_post = Post.objects.filter(
            is_auto_generated=True,
            title=title,
            created_at__year__in=[target_date.year, timezone.now().year]
        ).first()

        if existing_post and not force:
            skipped_posts.append({'title': title, 'post_id': existing_post.id, 'reason': 'already_exists'})
            continue

        try:
            custom_date_str = target_date.strftime("%B %d, %Y")
            relative_media_path = PosterGenerator.generate_poster(
                member=member,
                event_type=event_type,
                spouse=ev.get('spouse'),
                custom_date_str=custom_date_str
            )

            creator = member if not member.is_deceased else default_creator

            post = Post.objects.create(
                creator=creator,
                post_type='news',
                title=title,
                description=description,
                event_date=timezone.now(),
                is_auto_generated=True,
                visibility='public'
            )

            Media.objects.create(
                uploader=creator,
                post=post,
                media_url=relative_media_path,
                caption=title,
                media_type='image'
            )

            created_posts.append({'title': title, 'post_id': post.id, 'media_path': relative_media_path})
            logger.info(f"Auto-generated poster for {member.name} ({event_type}): Post #{post.id}")

        except Exception as e:
            logger.error(f"Failed to auto-generate poster for {member.name}: {e}")

    return {
        'status': 'success',
        'created': len(created_posts),
        'skipped': len(skipped_posts),
        'created_posts': created_posts,
        'skipped_posts': skipped_posts
    }


def ensure_daily_posters(force=False):
    """
    On-demand lightweight check for daily celebration posters.
    Uses cache/Redis locking so it only runs once per day and doesn't
    add latency to ongoing API requests.
    """
    today = date.today()
    cache_key = f"daily_posters_checked_{today.isoformat()}"

    if not force and cache.get(cache_key):
        return

    # Distributed lock to ensure only one thread/worker processes generation
    lock_key = f"lock_daily_posters_{today.isoformat()}"
    acquired = cache.add(lock_key, "1", timeout=60)
    if not acquired and not force:
        return

    try:
        run_daily_poster_generation(target_date=today, force=force)
        # Cache for 24 hours (86400 seconds)
        cache.set(cache_key, "1", timeout=86400)
    except Exception as e:
        logger.error(f"Error in ensure_daily_posters: {e}")
    finally:
        try:
            cache.delete(lock_key)
        except Exception:
            pass

