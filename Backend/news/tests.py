from django.test import TestCase
from django.contrib.auth import get_user_model
from families.models import Family, FamilyMember
from news.models import Post
from news.serializers import PostSerializer
from rest_framework.test import APIClient
import datetime

User = get_user_model()

class NewsTests(TestCase):
    def setUp(self):
        self.family = Family.objects.create(sl_no="1", branch="Main", member_no="M100")
        self.member = FamilyMember.objects.create(
            family=self.family,
            name="News Creator",
            age=30,
            relation="Head",
            date_of_birth=datetime.date(1990, 1, 1),
            blood_group="O+"
        )
        self.user = User.objects.create_user(username="creator", email="c@e.com", password="pass", member=self.member)
        self.client = APIClient()

    def test_post_serializer_author_id(self):
        post = Post.objects.create(
            creator=self.member,
            post_type='news',
            title='Test Title',
            description='Test Desc'
        )
        serializer = PostSerializer(post)
        self.assertEqual(serializer.data['author_id'], self.user.id)
        self.assertEqual(serializer.data['creator_name'], self.member.name)

    def test_news_create_logged_in(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/news/create/'
        data = {
            'title': 'API News',
            'description': 'API Desc',
            'post_type': 'news'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().creator, self.member)

    def test_news_create_not_linked(self):
        user_no_member = User.objects.create_user(username="no_member", email="nm@e.com", password="pass")
        self.client.force_authenticate(user=user_no_member)
        url = '/api/news/create/'
        data = {
            'title': 'Fail News',
            'description': 'Fail Desc',
            'post_type': 'news'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("linked to a Family Member", response.data['error'])

    def test_anniversary_detector_and_poster_command(self):
        from django.core.management import call_command
        from news.services.anniversary_detector import AnniversaryDetector

        # Set up a member with birthday on March 15
        bday_member = FamilyMember.objects.create(
            family=self.family,
            name="Birthday Star",
            age=25,
            relation="Member",
            date_of_birth=datetime.date(2001, 3, 15),
            blood_group="A+"
        )

        test_date = datetime.date(2026, 3, 15)
        events = AnniversaryDetector.get_events_for_date(test_date)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['event_type'], 'birthday')
        self.assertEqual(events[0]['member'], bday_member)

        # Run generate_daily_posters command
        call_command('generate_daily_posters', date='2026-03-15')
        self.assertEqual(Post.objects.filter(is_auto_generated=True).count(), 1)
        auto_post = Post.objects.filter(is_auto_generated=True).first()
        self.assertIn("Birthday Star", auto_post.title)
        self.assertEqual(auto_post.media.count(), 1)

        # Verify duplicate prevention: running again should not create a duplicate
        call_command('generate_daily_posters', date='2026-03-15')
        self.assertEqual(Post.objects.filter(is_auto_generated=True).count(), 1)

