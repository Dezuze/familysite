from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from rest_framework.test import APIClient


def _make_image_file(name: str = 'test.gif') -> SimpleUploadedFile:
    gif = (b'GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;')
    return SimpleUploadedFile(name, gif, content_type='image/gif')


from django.conf import settings
import tempfile
import shutil
from families.models import FamilyMember, Family

class ProfilesAPITestCase(TestCase):
    def setUp(self):
        self._tmp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._tmp_media

        User = get_user_model()
        self.family = Family.objects.create(sl_no='P1', branch='ProBranch', member_no='PMem1')
        self.member = FamilyMember.objects.create(family=self.family, first_name="Profile", last_name="User", date_of_birth="2000-01-01")
        self.user = User.objects.create_user(username='puser', email='p@example.com', member=self.member, password='pw')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        shutil.rmtree(self._tmp_media)

    def test_gallery_create_and_list(self):
        img = _make_image_file('gallery.gif')
        resp = self.client.post(
            '/api/profiles/gallery/',
            {'image': img, 'date': '2025-01-01', 'description': 'pic'},
        )
        self.assertEqual(resp.status_code, 201, msg=f"resp.data={resp.data}")
        resp2 = self.client.get('/api/profiles/gallery/')
        self.assertEqual(resp2.status_code, 200)
        data = resp2.data.get('results') if isinstance(resp2.data, dict) else resp2.data
        self.assertIsInstance(data, list)

    def test_committee_create_and_list(self):
        img = _make_image_file('committee.gif')
        resp = self.client.post(
            '/api/profiles/committee/',
            {'user': self.user.id, 'pic': img, 'role': 'organizer'},
        )
        self.assertEqual(resp.status_code, 201, msg=f"resp.data={resp.data}")
        resp2 = self.client.get('/api/profiles/committee/')
        self.assertEqual(resp2.status_code, 200)
        data = resp2.data.get('results') if isinstance(resp2.data, dict) else resp2.data
        self.assertIsInstance(data, list)
