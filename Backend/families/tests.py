from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.conf import settings
from django.contrib.auth import get_user_model
import tempfile
import shutil
from django.core.files.uploadedfile import SimpleUploadedFile
from families.models import Family, FamilyMedia, FamilyMember

User = get_user_model()


class FamilyMediaAPITest(APITestCase):
    def setUp(self):
        # temporary media root
        self._tmp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._tmp_media

        self.family = Family.objects.create(sl_no='S1', branch='B', member_no='Mtest')
        self.member = FamilyMember.objects.create(
            family=self.family, 
            name="Test User",
            age=30,
            relation="Head",
            date_of_birth="1990-01-01",
            education="B.Tech",
            occupation="Engineer",
            blood_group="O+"
        )
        self.user = User.objects.create_user(username='testuser', password='pass', member=self.member)
        self.client = APIClient()

    def tearDown(self):
        shutil.rmtree(self._tmp_media)

    def _get_image(self, name='test.gif'):
        gif = (b'GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;')
        return SimpleUploadedFile(name, gif, content_type='image/gif')

    def test_create_requires_auth(self):
        url = '/api/families/media/'
        data = {'family': self.family.id, 'category': 'family', 'image': self._get_image()}
        resp = self.client.post(url, data, format='multipart')
        # Should be unauthorized
        self.assertIn(resp.status_code, (401, 403))

    def test_crud_flow_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/families/media/'
        data = {'family': self.family.id, 'category': 'family', 'image': self._get_image('a.gif')}
        resp = self.client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, 201)
        created_id = resp.data['id']

        # list
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

        # retrieve
        resp = self.client.get(f'{url}{created_id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], created_id)

        # update (partial) using multipart to avoid parser mismatch in tests
        data2 = {'category': 'wedding'}
        resp = self.client.patch(f'{url}{created_id}/', data2, format='multipart')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['category'], 'wedding')

        # delete
        resp = self.client.delete(f'{url}{created_id}/')
        self.assertIn(resp.status_code, (204, 200))

        # final list count
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class ApiSmokeTests(TestCase):
    def test_apps_api_endpoints(self):
        client = APIClient()
        # news latest (type may not exist but endpoint should return 200/404 rather than crash)
        r = client.get('/api/news/latest/general/')
        self.assertIn(r.status_code, (200, 404))
        # profiles gallery and committee
        r = client.get('/api/profiles/gallery/')
        self.assertIn(r.status_code, (200, 404))
        r = client.get('/api/profiles/committee/')
        self.assertIn(r.status_code, (200, 404))
        # families base endpoint (GET may be not allowed but should not 500)
        r = client.get('/api/families/')
        self.assertNotEqual(r.status_code, 500)
        # Tree endpoint
        r = client.get('/api/families/tree/')
        self.assertEqual(r.status_code, 200)


class UserProfileAPITest(APITestCase):
    def setUp(self):
        self._tmp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._tmp_media
        
        self.family = Family.objects.create(sl_no='S2', branch='B2', member_no='M2')
        self.member = FamilyMember.objects.create(
            family=self.family, 
            name="Init Name",
            age=25,
            relation="Son",
            date_of_birth="2000-01-01",
            education="Student",
            occupation="None",
            blood_group="A+"
        )
        self.user = User.objects.create_user(username='newuser', password='pass', member=self.member)
        self.member.user = self.user
        self.member.save()
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        shutil.rmtree(self._tmp_media)

    def _get_image(self, name='profile.jpg'):
        img = (b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00')
        return SimpleUploadedFile(name, img, content_type='image/jpeg')

    def test_onboarding_update_persistence(self):
        url = '/api/families/profile/'
        data = {
            'name': 'Updated Person',
            'gender': 'F',
            'date_of_birth': '1995-05-05',
            'profile_pic': self._get_image('new_pic.jpg'),
            'bio': 'My Bio',
            'email_id': 'updated@test.com'
        }
        
        resp = self.client.post(url, data, format='multipart')
        self.assertEqual(resp.status_code, 200)
        
        self.member.refresh_from_db()
        self.assertEqual(self.member.name, 'Updated Person')
        self.assertEqual(self.member.gender, 'F')
        self.assertEqual(self.member.bio, 'My Bio')
        self.assertEqual(self.member.email_id, 'updated@test.com')
        self.assertTrue(bool(self.member.photo))
        
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'], 'Updated Person')
        self.assertEqual(resp.data['gender'], 'F')
        self.assertEqual(resp.data['bio'], 'My Bio')
        self.assertIn('new_pic', resp.data['photo'])
